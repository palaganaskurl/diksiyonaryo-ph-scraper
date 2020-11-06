import json
import unidecode


if __name__ == '__main__':
    with open('../words/tagalog-words.json', 'r', encoding='utf-8') as f:
        words = json.load(f)

        new_words = {}

        for word, details in words.items():
            new_definitions = []

            for definition in details['definitions'][:]:
                new_definitions.append(unidecode.unidecode(definition))

            details['definitions'] = new_definitions
            new_words[unidecode.unidecode(word)] = details

        with open('../words/tagalog-words-decoded.json', 'w+', encoding='utf-8') as g:
            json.dump(new_words, g, ensure_ascii=False)
