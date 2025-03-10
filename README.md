# Wikipedia To Markdown

This is a simple script to convert a Wikipedia article to Markdown.

## Prerequisites

- Python 3

## Installation

```bash
git clone
cd wikipedia-markdown-generator
pip3 install -r requirements.txt
```

## Usage

```bash
python3 wiki-to-md.py <topic_name>
```

Specifying if you want to download the images is optional. It is set to `yes` 
by default, you can set it to `no`.

```bash
python3 wiki-to-md.py --download-images=no <topic_name>
```

Optional comma seperated list of languages. 
The topic is searched for in order of the given languages.
The default is `["de", "en"]`.

```bash
python3 wiki-to-md.py -- <topic_name>
```

For help:

```bash
python3 wiki-to-md.py --help
```

## Output

The output is a Markdown file with the same name as the topic name under the newly created directory named after the topic. Images will be placed inside `topic/images/`.

## Why?

I wanted to convert some Wikipedia articles to Markdown for my personal notes. I couldn't find a simple script to do this, so I wrote one myself.

## Fork from [erictherobot](https://github.com/erictherobot)
I'm very thankful for the initial pointers by [erictherobot](https://github.com/erictherobot).
I started this project with the code provided by [erictherobot](https://github.com/erictherobot) in [erictherobot/wikipedia-markdown-generator](https://github.com/erictherobot/wikipedia-markdown-generator). 
On my way I decided to do a full rewrite and to only keep some very small parts.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
