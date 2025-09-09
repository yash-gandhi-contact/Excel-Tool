# # modules/webpage_finder.py
# import streamlit as st
# import pandas as pd
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse, unquote
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# from io import BytesIO
# import urllib3

# # Silence insecure request warnings when we intentionally use verify=False fallback
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# def get_session(retries: int = 2, backoff_factor: float = 0.3, status_forcelist=(429, 500, 502, 503, 504)):
#     """Create a requests.Session with retry strategy and a browser-like user agent."""
#     session = requests.Session()
#     retry = Retry(
#         total=retries,
#         read=retries,
#         connect=retries,
#         backoff_factor=backoff_factor,
#         status_forcelist=status_forcelist,
#         allowed_methods=frozenset(["HEAD", "GET", "OPTIONS"])
#     )
#     adapter = HTTPAdapter(max_retries=retry)
#     session.mount("https://", adapter)
#     session.mount("http://", adapter)
#     session.headers.update({
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                       "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
#     })
#     return session


# def clean_url(raw_url: str):
#     """Normalize and clean the URL. Return None if invalid."""
#     if raw_url is None:
#         return None
#     url = str(raw_url).strip()
#     if not url:
#         return None

#     # decode percent encoding and strip common trailing/leading junk
#     url = unquote(url)
#     url = url.strip(" '\";,\n\r\t")
#     url = url.replace("%20", "")
#     url = url.replace(" ", "")

#     # If the user pasted something like "example.com" or "www.example.com", add scheme
#     parsed = urlparse(url)
#     if not parsed.scheme:
#         url = "https://" + url
#         parsed = urlparse(url)

#     # After parsing, ensure a network location exists
#     if not parsed.netloc:
#         return None

#     return url


# def fetch_with_fallback(session: requests.Session, url: str, timeout: int = 10):
#     """
#     Try to fetch a URL with:
#       1) verify=True (normal SSL validation)
#       2) verify=False (if SSL errors)
#       3) if https and fails, try http:// (verify=False)
#     Raises the last exception if everything fails.
#     Returns requests.Response on success.
#     """
#     # Attempt 1: normal GET with SSL verification
#     try:
#         resp = session.get(url, timeout=timeout, verify=True)
#         resp.raise_for_status()
#         return resp
#     except requests.exceptions.SSLError as ssl_err:
#         # Try again without verifying certificate
#         try:
#             resp = session.get(url, timeout=timeout, verify=False)
#             resp.raise_for_status()
#             return resp
#         except Exception:
#             # move to next fallback below
#             pass
#     except Exception:
#         # other exceptions (timeout, connection error) handled in next steps
#         pass

#     # If URL uses https://, try http:// fallback (without verify)
#     parsed = urlparse(url)
#     if parsed.scheme == "https":
#         http_url = "http://" + parsed.netloc + parsed.path or ""
#         try:
#             resp = session.get(http_url, timeout=timeout, verify=False)
#             resp.raise_for_status()
#             return resp
#         except Exception as e:
#             # re-raise most recent for caller to handle/log
#             raise e

#     # If nothing worked, raise a generic RequestException so caller logs the error.
#     raise requests.exceptions.RequestException(f"Failed to fetch {url}")


# def find_subpages(main_url: str, keywords: list, session: requests.Session, limit: int = 5, timeout: int = 10):
#     """
#     Visit main_url and return up to `limit` subpage URLs (absolute) matching any keyword
#     in either the href or the link text. Returns a tuple: (found_list, error_message_or_empty).
#     """
#     found = []
#     try:
#         resp = fetch_with_fallback(session, main_url, timeout=timeout)
#         html = resp.text
#         soup = BeautifulSoup(html, "html.parser")

#         # extract links and test keywords
#         for a in soup.find_all("a", href=True):
#             href = a.get("href").strip()
#             # skip non-http links
#             if href.lower().startswith(("mailto:", "tel:", "javascript:")):
#                 continue
#             # build absolute URL
#             full = urljoin(resp.url, href)
#             # normalize basic trailing fragments
#             full = full.split('#')[0].strip()
#             if not full:
#                 continue

#             low_full = full.lower()
#             low_text = (a.get_text() or "").lower()

#             if any(kw.lower() in low_full or kw.lower() in low_text for kw in keywords):
#                 # skip duplicates
#                 if full not in found:
#                     found.append(full)
#                 if len(found) >= limit:
#                     break

#         return found, ""
#     except Exception as e:
#         # return empty found list and error message (caller will log)
#         return [], str(e)


# def render_webpage_finder_page():
#     st.subheader("🌐 Webpage Finder")

#     uploaded_file = st.file_uploader("Upload an Excel file with URLs", type=["xlsx", "xls"])
#     if uploaded_file is None:
#         st.info("Please upload an Excel file to proceed.")
#         return

#     try:
#         df = pd.read_excel(uploaded_file)
#     except Exception as e:
#         st.error(f"Error reading the Excel file: {e}")
#         return

#     st.success("✅ File loaded")
#     st.dataframe(df, use_container_width=True)

#     # Select which column contains URLs
#     url_column = st.selectbox("Select the column containing URLs", options=list(df.columns))
#     keywords_input = st.text_area("Enter keywords (comma separated)", placeholder="e.g. contact, about, impressum, services")
#     keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

#     # Optional settings
#     st.sidebar.markdown("**Processing options**")
#     timeout = st.sidebar.number_input("Request timeout (seconds)", min_value=3, max_value=60, value=12)
#     max_rows = st.sidebar.number_input("Max rows to process (0 = all)", min_value=0, value=0)
#     limit_per_site = st.sidebar.number_input("Max matches per main URL", min_value=1, max_value=20, value=5)
#     start_button = st.button("🔍 Start Finding Webpages")

#     if not start_button:
#         st.info("Configure options and click 'Start Finding Webpages'.")
#         return

#     if not keywords:
#         st.warning("Please provide at least one keyword to search for.")
#         return

#     # Prepare URL list
#     raw_urls = df[url_column].dropna().tolist()
#     if max_rows and max_rows > 0:
#         raw_urls = raw_urls[:max_rows]

#     total = len(raw_urls)
#     if total == 0:
#         st.warning("No URLs found in the selected column.")
#         return

#     session = get_session(retries=2, backoff_factor=0.4)
#     progress_bar = st.progress(0)
#     status = st.empty()

#     results = []
#     for idx, raw in enumerate(raw_urls, start=1):
#         try:
#             status.info(f"Processing {idx}/{total}: {raw}")
#         except Exception:
#             # in rare cases raw may be not displayable
#             status.info(f"Processing {idx}/{total}")

#         cleaned = clean_url(raw)
#         if not cleaned:
#             results.append({
#                 "Main URL": raw,
#                 "Cleaned URL": "",
#                 "Found": [],
#                 "Error": "Invalid/empty URL after cleaning"
#             })
#             progress_bar.progress(idx/total)
#             continue

#         found_list, error = find_subpages(cleaned, keywords, session=session, limit=limit_per_site, timeout=timeout)
#         results.append({
#             "Main URL": raw,
#             "Cleaned URL": cleaned,
#             "Found": found_list,
#             "Error": error
#         })

#         progress_bar.progress(idx/total)

#     # Build result DataFrame and expand found URLs into separate columns
#     out = pd.DataFrame(results)
#     max_found_cols = limit_per_site
#     for i in range(max_found_cols):
#         col_name = f"Found URL {i+1}"
#         out[col_name] = out["Found"].apply(lambda lst: lst[i] if isinstance(lst, list) and len(lst) > i else "")

#     # Keep ordering / useful columns
#     display_cols = ["Main URL", "Cleaned URL"] + [f"Found URL {i+1}" for i in range(max_found_cols)] + ["Error"]
#     out_display = out[display_cols]

#     st.subheader("📊 Results")
#     st.dataframe(out_display, use_container_width=True)

#     # Summary counts
#     total_matches = out["Found"].apply(lambda lst: len(lst) if isinstance(lst, list) else 0).sum()
#     st.markdown(f"**Total URLs processed:** {total}  •  **Total matches found:** {total_matches}")

#     # Show errors separately (if any)
#     errors_df = out[out["Error"].astype(bool)][["Main URL", "Cleaned URL", "Error"]]
#     if not errors_df.empty:
#         st.subheader("⚠️ Errors / Warnings")
#         st.dataframe(errors_df, use_container_width=True)

#     # Download as Excel
#     to_download = out_display.copy()
#     to_download = to_download.fillna("")  # avoid NaN
#     buffer = BytesIO()
#     with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
#         to_download.to_excel(writer, index=False, sheet_name="Results")
#     buffer.seek(0)

#     st.download_button(
#         label="📥 Download results as Excel",
#         data=buffer.getvalue(),
#         file_name="webpage_finder_results.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     status.success("Processing completed.")


import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from io import BytesIO

def clean_url(url: str) -> str:
    """Ensure URLs have scheme and are stripped of spaces."""
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url

def make_session(timeout: int):
    """Return a requests session with retries and SSL handling."""
    session = requests.Session()
    retry = Retry(
        total=2, backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.verify = False  # Disable SSL verification
    return session

def find_matching_subpages(base_url, main_keywords, secondary_keywords, avoid_keywords, timeout, max_matches):
    """Find subpages containing main keywords and secondary keywords, avoid unwanted keywords."""
    session = make_session(timeout)
    found_urls = []
    start_time = time.time()

    try:
        response = session.get(base_url, timeout=timeout)
        if response.status_code != 200:
            return found_urls

        soup = BeautifulSoup(response.text, "html.parser")
        links = set(
            urljoin(base_url, a.get("href"))
            for a in soup.find_all("a", href=True)
        )

        for link in links:
            # stop if 10 minutes exceeded
            if time.time() - start_time > 300:
                break

            if len(found_urls) >= max_matches:
                break

            # avoid unwanted URLs
            if any(kw.lower() in link.lower() for kw in avoid_keywords):
                continue

            # Step 1: check if link matches main keywords
            if any(kw.lower() in link.lower() for kw in main_keywords):
                try:
                    sub_resp = session.get(link, timeout=timeout)
                    if sub_resp.status_code == 200:
                        text = sub_resp.text.lower()
                        # Step 2: check for secondary keywords
                        if any(kw.lower() in text for kw in secondary_keywords):
                            found_urls.append(link)
                except Exception:
                    continue
    except Exception:
        pass

    return found_urls[:max_matches]

def render_webpage_finder_page():
    st.markdown("<h2 style='text-align: center;'>Webpage Finder</h2>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Excel file with URLs", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("### Uploaded Data")
        st.dataframe(df)

        url_column = st.selectbox("Select the column containing URLs", df.columns)

        main_keywords_input = st.text_area("Enter MAIN keywords (to filter subpages)", "contact, about, impressum")
        secondary_keywords_input = st.text_area("Enter SECONDARY keywords (to search inside subpages)", "email, phone")
        avoid_keywords_input = st.text_area("Enter AVOID keywords (skip URLs containing these)", "career, job")

        timeout = st.number_input("Request timeout (seconds)", min_value=5, max_value=60, value=10)
        max_rows = st.number_input("Max rows to process (0 = all)", min_value=0, value=0)
        max_matches = st.number_input("Max matches per main URL", min_value=1, max_value=10, value=5)

        if st.button("Process"):
            urls = df[url_column].dropna().tolist()
            if max_rows > 0:
                urls = urls[:max_rows]

            main_keywords = [kw.strip() for kw in main_keywords_input.split(",") if kw.strip()]
            secondary_keywords = [kw.strip() for kw in secondary_keywords_input.split(",") if kw.strip()]
            avoid_keywords = [kw.strip() for kw in avoid_keywords_input.split(",") if kw.strip()]

            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            total = len(urls)
            for idx, url in enumerate(urls, start=1):
                clean = clean_url(url)
                status_text.text(f"Processing {idx}/{total}: {clean}")
                matches = find_matching_subpages(clean, main_keywords, secondary_keywords, avoid_keywords, timeout, max_matches)

                row = {"Main URL": url}
                for i, m in enumerate(matches, start=1):
                    row[f"Result {i}"] = m
                results.append(row)

                progress_bar.progress(idx / total)

            if results:
                result_df = pd.DataFrame(results)
                st.write("### Results")
                st.dataframe(result_df)

                # Download option
                def convert_df_to_excel(df):
                    output = BytesIO()
                    df.to_excel(output, index=False, engine="openpyxl")
                    output.seek(0)
                    return output

                excel_data = convert_df_to_excel(result_df)
                st.download_button(
                    "Download results as Excel",
                    data=excel_data,
                    file_name="webpage_finder_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No matches found for the given keywords.")
