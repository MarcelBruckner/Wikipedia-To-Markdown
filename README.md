# Wikipedia To Markdown

This is a simple script to convert a Wikipedia article to Markdown.

## Why?

I wanted to convert some Wikipedia articles to Markdown for my personal notes. I couldn't find a simple script to do this, so I wrote one myself. 
I drew some inspiration from [erictherobot/wikipedia-markdown-generator](https://github.com/erictherobot/wikipedia-markdown-generator) but ended up rewriting it completely. 
I especially took the time to **properly format math expressions to be compatible with markdown**.

## Prerequisites

- Python 3

## Installation

```bash
git clone git@github.com:MarcelBruckner/Wikipedia-To-Markdown.git
cd Wikipedia-To-Markdown
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
Generate a markdown file for a provided topic.

positional arguments:
  topic                 The topic to generate a markdown file for.

options:
  -h, --help            show this help message and exit
  --download_images, --no-download_images
                        Specify whether to not download images.
                        Default: True
  --languages LANGUAGES
                        Specify the languages to look for the topic.
                        Default: de,en
  --output OUTPUT       The output path for the markdown and images.
                        Default: /output
```

## Docker Image

There is a public image on Docker Hub: [marcelbruckner/wikipedia-to-markdown](https://hub.docker.com/repository/docker/marcelbruckner/wikipedia-to-markdown). Run it via:

```bash
docker run \
         --volume ./docker:/output \  
         wikipedia-to-markdown \
         "topic"
         <options>
```

## Output

The output is a Markdown file with the same name as the topic name under the newly created directory named after the topic. Images will be placed inside `output/topic/images/`.

## Fork from [erictherobot](https://github.com/erictherobot)
I'm very thankful for the initial pointers by [erictherobot](https://github.com/erictherobot).
I started this project with the code provided by [erictherobot](https://github.com/erictherobot) in [erictherobot/wikipedia-markdown-generator](https://github.com/erictherobot/wikipedia-markdown-generator). 
On my way I decided to do a full rewrite and to only keep some very small parts.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
