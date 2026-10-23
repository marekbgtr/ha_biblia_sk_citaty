"""Parse references and public Biblia.sk HTML without external dependencies."""
from dataclasses import dataclass
from html.parser import HTMLParser
import re

LABELS = {'mk': 'Mk', 'mt': 'Mt', 'lk': 'Lk', 'jn': 'Jn', '1kor': '1 Kor', 'rim': 'Rim', 'flp': 'Flp', 'z': 'Ž'}

@dataclass(frozen=True)
class Passage:
    book: str
    chapter: int
    first: int
    last: int

    @property
    def url(self):
        return f'https://biblia.sk/citanie/bot/{self.book}/{self.chapter}'

    @property
    def reference(self):
        verses = str(self.first) if self.first == self.last else f'{self.first}–{self.last}'
        return f'{LABELS.get(self.book, self.book)} {self.chapter},{verses}'


def parse_passages(value):
    if not isinstance(value, str) or len(value) > 20000:
        raise ValueError('Invalid reference list')
    result = []
    for line in value.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.fullmatch(r'([1-3]?[a-z]{1,8})\s+(\d{1,3}):(\d{1,3})(?:-(\d{1,3}))?', line.lower())
        if not match:
            raise ValueError('Use one reference per line, for example mk 1:14-15')
        book, chapter, first, last = match.groups()
        chapter, first, last = int(chapter), int(first), int(last or first)
        if not (1 <= chapter <= 150 and 1 <= first <= last <= 176 and last-first < 50):
            raise ValueError('Invalid chapter or verse range (maximum 50 verses)')
        result.append(Passage(book, chapter, first, last))
    if not 1 <= len(result) <= 366:
        raise ValueError('Provide between 1 and 366 passages')
    return result


class VerseParser(HTMLParser):
    def __init__(self, chapter):
        super().__init__(convert_charrefs=True)
        self.chapter = str(chapter)
        self.verses = {}
        self.depth = 0
        self.skip = 0
        self.number = None
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'span':
            if self.depth:
                self.depth += 1
            elif attrs.get('data-chapter') == self.chapter and attrs.get('data-verse', '').isdigit():
                self.number = int(attrs['data-verse'])
                self.depth = 1
                self.parts = []
        if self.depth and tag == 'sup':
            self.skip += 1
        if self.depth and tag == 'br':
            self.parts.append(' ')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'sup' and self.skip:
            self.skip -= 1
        if tag == 'span' and self.depth:
            self.depth -= 1
            if not self.depth:
                self.verses[self.number] = ' '.join(''.join(self.parts).split())
                self.number = None

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.parts.append(data)


def extract_text(html, passage):
    parser = VerseParser(passage.chapter)
    parser.feed(html)
    verses = [parser.verses.get(n, '') for n in range(passage.first, passage.last + 1)]
    if not all(verses):
        raise ValueError('Requested verses are missing; check reference or changed HTML')
    return '\n\n'.join(verses)
