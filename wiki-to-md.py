import os
import wikipedia
import argparse
import requests
import urllib.parse
import wikipediaapi
import concurrent.futures

def url(text: str, link: str) -> str:
    """
    Generates a Markdown-formatted URL.

    Args:
        text (str): The display text for the link.
        link (str): The URL to which the link points.

    Returns:
        str: A Markdown-formatted link in the format "[text](link)".

    Example:
        >>> url("Google", "https://www.google.com")
        '[Google](https://www.google.com)'
    """
    return f"[{text}]({link})"

def heading(text: str, depth: int) -> str:
    """
    Generates a Markdown heading.

    Args:
        text (str): The heading text.
        depth (int): The heading level (number of '#' symbols).

    Returns:
        str: A Markdown-formatted heading with the specified depth.

    Example:
        >>> heading("Title", 2)
        '## Title\\n\\n'
    """
    return "#" * depth + " " + text + "\n\n"

def section(value: wikipediaapi.WikipediaPageSection | list[wikipediaapi.WikipediaPageSection]) -> str:
    """
    Processes a Wikipedia page section or a list of sections and converts them into Markdown format.

    - If a list of sections is provided, it iterates through each section and recursively processes them.
    - If a single section is provided, it formats its title as a Markdown heading, where the heading level is determined 
      by the section's depth in the Wikipedia page hierarchy.
    - The section's content is cleaned and formatted for Markdown compatibility.
    - Any subsections within the section are also processed recursively and appended to the Markdown output.

    Args:
        value (wikipediaapi.WikipediaPageSection | list[wikipediaapi.WikipediaPageSection]): 
            A single Wikipedia page section or a list of sections.

    Returns:
        str: A string containing the Markdown representation of the section(s).

    Example:
        Given a Wikipedia section titled "Introduction" with a depth level of 1 and text "This is an intro.",
        the function will return:

        '# Introduction\\n\\nThis is an intro.\\n\\n'

    Notes:
        - When processing subsections, they are appended to the Markdown output after the parent section.
        - If multiple sections are provided as a list, they are all processed and concatenated into a single Markdown string.
    """
    if type(value) is list:
        markdown = "".join(section(v) for v in value)
        return markdown

    markdown = heading(value.title, value.level + 1)
    markdown += sanitize_text(value.text)
    markdown += "\n\n" + section(value.sections)

    return markdown

def find_first_start_of_math(lines: list[str]) -> int:
    """
    Identifies the starting index of a mathematical expression in a list of lines.

    This function scans through the given lines to determine where a math block begins.
    It assumes that an empty line signals the potential start of a math block.
    If more than two consecutive lines follow the empty line, it is considered the start of a display-style math block.

    Args:
        lines (list[str]): A list of text lines to analyze.

    Returns:
        int: The index of the first detected math block (-1 if none is found).

    Example:
        >>> lines = ["Some text", "", "x^2 + y^2 = z^2", "More text"]
        >>> find_first_start_of_math(lines)
        1

    Notes:
        - The function assumes that an empty line signals the start of a possible math block.
        - If fewer than two following lines are found, it resets the detection process.
    """
    start_index = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if stripped is not line and start_index == -1:
                start_index = i
        else:
            if start_index >= 0 :
                if i - start_index > 2:
                    return start_index 
                else:
                    start_index = -1

    return -1
    
def find_end_of_math(lines: list[str]) -> tuple[int, str]:
    """
    Identifies the ending index of a mathematical expression in a list of lines.

    This function scans through a list of lines to detect the end of a math block, 
    particularly looking for the presence of '\\displaystyle', which marks the beginning 
    of a display-style equation.

    - If '\\displaystyle' is found, its index and content are stored.
    - The function continues scanning until an empty or whitespace-only line appears, 
      which signals the end of the math block.

    Args:
        lines (list[str]): A list of strings representing lines of text.

    Returns:
        tuple[int, str]: A tuple containing:
            - The index of the first line after the math block.
            - The content of the detected display-style math expression.

    Example:
        >>> lines = ["Some text", "\\displaystyle x^2 + y^2 = z^2", "", "More text"]
        >>> find_end_of_math(lines)
        (2, "\\displaystyle x^2 + y^2 = z^2")

    Notes:
        - If no empty line follows '\\displaystyle', the function assumes the math 
          block continues until the end of the text.
        - Returns an index one position beyond the last processed math block line.
    """
    displaystyle_index = -1
    displaystyle = ""
    for i, line in enumerate(lines):
        if "\\displaystyle" in line:
            displaystyle_index = i
            displaystyle = line
            continue

        if displaystyle_index >= 0 and (not line or line.strip()):
            return i, displaystyle
    return i + 1, displaystyle

def convert_displaystyle(displaystyle: str) -> str:
    """
    Converts a LaTeX display-style math expression to a Markdown-compatible format.

    This function removes `\\displaystyle` from the beginning of the input and wraps 
    the remaining math expression with appropriate dollar sign delimiters.

    Args:
        displaystyle (str): The LaTeX display-style math expression to convert.

    Returns:
        str: The formatted mathematical expression wrapped with the appropriate delimiters.

    Example:
        >>> convert_displaystyle("\\displaystyle x^2 + y^2 = z^2")
        "$x^2 + y^2 = z^2$"

    Notes:
        - The function assumes that the input starts with `\\displaystyle` and removes it before formatting.
        - The output format depends on the style of the mathematical expression.
    """
    markdown = displaystyle.strip()

    symbol = "$"

    markdown = symbol + markdown[1:]
    markdown = markdown[:-1] + symbol

    return markdown

def sanitize_text(text: str) -> str:
    """
    Cleans and processes the input text for proper Markdown formatting.

    This function detects mathematical expressions, replaces them with properly formatted 
    Markdown-compatible LaTeX math syntax, and adjusts text spacing.

    Args:
        text (str): The input text to be processed.

    Returns:
        str: The cleaned and formatted text with adjusted spacing and properly formatted math expressions.

    Notes:
        - Consecutive newline characters are preserved to maintain paragraph structure.
        - Mathematical expressions enclosed in `\\displaystyle` are detected and replaced.
    """
    lines = text.split("\n")
    
    start_index = -1

    while True:
        start_index = find_first_start_of_math(lines)
        if start_index < 0:
            break

        length, displaystyle = find_end_of_math(lines[start_index:])

        for _ in range(length):
            del lines[start_index]

        lines.insert(start_index, convert_displaystyle(displaystyle))
        print("")
        
    result = "\n".join(lines)
    result = result.replace(".", ".\n")
    return result

def get_page_for_topic(topic: str, languages: list[str]) -> wikipediaapi.WikipediaPage:
    """
    Retrieves a Wikipedia page for the given topic, checking multiple languages.
 
    This function attempts to fetch the Wikipedia page for a given topic by searching 
    in the specified list of languages. It returns the first available page.
 
    Args:
        topic (str): The topic to search for on Wikipedia.
        languages (list[str]): A list of language codes (e.g., ["de", "en"]) to search in order.
 
    Returns:
        wikipediaapi.WikipediaPage: The Wikipedia page object for the requested topic.
 
    Raises:
        wikipedia.exceptions.PageError: If the topic does not exist in any of the specified languages.
 
    Notes:
        - The function iterates through the languages in order and returns the first available page.
        - If the page does not exist in any of the specified languages, an exception is raised.
    """
    for language in languages:
        wiki_wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language=language, extract_format=wikipediaapi.ExtractFormat.WIKI)
        page = wiki_wiki.page(topic)
        if page.exists():
            return page
    raise wikipedia.exceptions.PageError

def replace_links(markdown_text: str, links: wikipediaapi.PagesDict) -> str:
    """
    Replaces Wikipedia link references in the Markdown text with their full URLs.

    This function asynchronously fetches Wikipedia page URLs for provided link names 
    and replaces their occurrences in the Markdown text with properly formatted 
    Markdown links.

    Args:
        markdown_text (str): The original Markdown content.
        links (wikipediaapi.PagesDict): A dictionary mapping link names to Wikipedia pages.

    Returns:
        str: The updated Markdown text with links replaced.

    Notes:
        - The function utilizes threading for concurrent URL fetching to optimize performance.
        - If a URL cannot be retrieved, the link remains unchanged in the text.
    """
    def get_full_url(p: wikipediaapi.WikipediaPage):
        return p.fullurl
    
    result = markdown_text
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_url = {executor.submit(get_full_url, link): name for name, link in links.items()}
        for future in concurrent.futures.as_completed(future_to_url):
            name = future_to_url[future]
            try:
                fullurl = future.result()
                result = result.replace(name, url(name, fullurl))
            except Exception:
                pass

    return result

def generate_markdown(topic: str, download_images: bool, languages: list[str]) -> str | None:
    """
    Generates a Markdown file for a given Wikipedia topic.
 
    This function retrieves the Wikipedia page for the given topic in one of the specified 
    languages, processes its content, and formats it into Markdown. It includes a summary, 
    sections, references, and the page URL. Optionally, images can be downloaded and embedded.
 
    Args:
        topic (str): The topic to generate a Markdown file for.
        download_images (bool): Whether to download and embed images in the Markdown file.
        languages (list[str]): A list of language codes to search for the topic.
 
    Returns:
        str | None: The filename of the generated Markdown file or None if the page does not exist.
 
    Notes:
        - If the topic leads to a disambiguation page, available options are printed, and the function exits.
        - If the page is not found, an error message is displayed.
        - The function prioritizes searching in the provided languages order.
    """
    try:
        wikipedia_page = wikipedia.page(title=topic)
        wikipediaapi_page = get_page_for_topic(topic, languages)
    except wikipedia.exceptions.DisambiguationError as e:
        print(e.options)
        return None
    except wikipedia.exceptions.PageError:
        print(f"Page not found for the topic: {topic}")
        return None

    markdown_text: str = heading(url(topic, wikipedia_page.url), 1)

    markdown_text += heading("Summary", 2)
    markdown_text += sanitize_text(wikipediaapi_page.summary) + "\n\n"
    
    markdown_text += section(list(section for section in wikipediaapi_page.sections if section not in ["See also", "References", "Further reading"]))

    markdown_text += heading("References", 2)
    markdown_text += "\n".join(f'- {x}' for x in wikipedia_page.references)
    markdown_text += "\n\n"

    markdown_text += heading("URL", 2)
    markdown_text += wikipedia_page.url
    markdown_text += "\n\n"

    markdown_text = replace_links(markdown_text, wikipediaapi_page.links)

    filename = write_page(topic, markdown_text, wikipedia_page.images, download_images)

    print(f"Markdown file created: {filename}")
    return filename

def write_page(topic: str, markdown_text: str, images: list[str], download_images: bool) -> str:
    """
    Writes the generated Markdown content to a file and optionally downloads images.

    This function creates a Markdown file for the given topic and saves the formatted 
    text. If `download_images` is enabled, it also downloads images and stores them 
    in an organized directory structure.

    Args:
        topic (str): The Wikipedia topic.
        markdown_text (str): The Markdown-formatted content.
        images (list[str]): A list of image URLs to be downloaded and embedded.
        download_images (bool): Whether to download images.

    Returns:
        str: The filename of the saved Markdown file.

    Notes:
        - If images are downloaded, they are saved in a subdirectory named after the topic.
        - The function ensures that necessary directories exist before saving images.
        - Each downloaded image is referenced in the Markdown file.
    """
    output_directory = ""
    if download_images:
        # Create a directory for markdown files
        output_directory = topic
        os.makedirs(output_directory, exist_ok=True)
        # Create a directory for image files
        image_directory = os.path.join(output_directory, "images")
        os.makedirs(image_directory, exist_ok=True)

        for image_url in images:
            image_filename = urllib.parse.unquote(os.path.basename(image_url))
            image_path = os.path.join(image_directory, image_filename)
            image_data = requests.get(image_url).content
            with open(image_path, "wb") as image_file:
                image_file.write(image_data)
            markdown_text += heading("Images", 2)
            markdown_text += f"![{image_filename}](./images/{image_filename})\n"

    filename = os.path.join(output_directory, f'{topic.replace(" ", "_")}.md')

    with open(filename, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_text)
    return filename


def parser() -> argparse.ArgumentParser:
    """
    Creates and configures an argument parser for command-line execution.
 
    This function sets up an argument parser that allows users to specify:
    - The topic they want to generate a Markdown file for.
    - Whether to download images.
    - The list of languages to search in.
 
    Returns:
        argparse.ArgumentParser: A configured argument parser instance.
 
    Notes:
        - The `topic` argument is required.
        - The `--download-images` argument allows users to enable or disable image downloads.
        - The `--languages` argument specifies the languages in which to look for the topic.
    """
    parser = argparse.ArgumentParser(
        description="Generate a markdown file for a provided topic."
    )
    parser.add_argument(
        "topic",
        type=str,
        help="The topic to generate a markdown file for.",
    )
    parser.add_argument(
        "--download-images",
        choices=['yes', 'no'],
        default='yes',
        help="Specify whether to download images (yes or no).",
    )
    parser.add_argument(
        "--languages",
        type=str,
        default='de,en',
        help="Specify the languages to look for the topic.",
    )
    return parser

args = parser().parse_args()

topic = args.topic
download_images = args.download_images == 'yes'
languages = args.languages.split(",")

generate_markdown(topic, download_images, languages)
