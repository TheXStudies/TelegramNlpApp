from collections import defaultdict
from heapq import nlargest

import matplotlib.pylab as plt
import numpy as np
from natasha import (
    Doc, Segmenter, NewsMorphTagger, NewsEmbedding, NewsSyntaxParser,
    MorphVocab
)


def process_messages(messages):
    """
    Обрабатываем текст сообщений с помощью NLP-библиотеки, группируем данные
    по нормализированным словам (леммам) и авторам
    и отображаем в виде графика
    :param messages: список либо iterable из сообщений
    :return: None
    """

    # структуры из библиотеки Natasha для обработки текста
    # используем нативные
    embedding = NewsEmbedding()
    # морфологический словарь
    morph_vocab = MorphVocab()

    # словарь словарей, а именно
    # {
    #     '12345': {
    #         'питон': 28,
    #         'делать': 18,
    #         ....
    #     },
    #     '53285': {
    #         'код': 13,
    #         'хороший': 5,
    #     ....
    # }
    #
    # Здесь 12345 - это айди автора сообщения, для каждого есть словарь из
    # лемм и частоты их использования
    lemmas_by_authors = defaultdict(lambda: defaultdict(int))
    for i, msg in enumerate(messages):
        # ограничитель на кол-во обрабатываемых сообщений. Настраивайте под себя
        if i == 300:
            break
        # сообщение может быть без текста, если там просто картинка или голосовалка
        if not msg['message']:
            continue

        # Превращаем текст в обьект, с которым мы можем работать
        doc = Doc(msg['message'])
        # сегментируем
        doc.segment(Segmenter())
        # морфологическая обработка
        doc.tag_morph(NewsMorphTagger(embedding))
        # синтаксис (понятно из названия функции, да? )
        doc.parse_syntax(NewsSyntaxParser(embedding))

        for t in doc.tokens:
            # некоторые части нам не нужны. Например, пунктуация, соединяюще слова,
            # такие как "не", "от", "на", нераспознанные и т.п, не несущие полезной
            # смысловой нагрузки
            if t.pos not in [
                    'PUNCT', 'NUM', "ADP", 'CCONJ', 'SCONJ', "PRON",
                    'ADV', "PART", "SYM", "DET", "ADJ", "AUX", "X"]:
                # собственно получаем лемму, т.е. нормализированную форму слова
                t.lemmatize(morph_vocab)
                # для автора данного сообщения для этой леммы увеличиваем счётчик
                lemmas_by_authors[msg['author']][t.lemma] += 1

    # если обрабатывать много сообщений, то будет много авторов.
    # мы выберем только авторов с максимальным количеством авторов
    lemmas_by_authors = dict(
        nlargest(
            16,  # сколько записей взять
            # какие записи обрабатывать. `items()` вернёт нам в виде пар "ключ"-"значение"
            lemmas_by_authors.items(),
            # как именно выбирать максимальное значение
            # в каждой паре мы возьмём количества лемм для автора и просуммируем
            key=lambda author_and_lemmas: sum(author_and_lemmas[1].values())))

    # ещё нам нужен общий список лемм для отображения на графике
    all_lemmas = defaultdict(int)
    for lemmas in lemmas_by_authors.values():
        for lemma, lcount in lemmas.items():
            all_lemmas[lemma] += lcount

    # аналогично как выше, только для общего списка лемм
    all_lemmas = dict(nlargest(
        30,
        all_lemmas.items(),
        key=lambda lemma_and_count: lemma_and_count[1],
    ))
    # повернуть названия лемм на графике, что бы они помещались
    plt.xticks(rotation=90)
    for author, lemmas in lemmas_by_authors.items():
        # для каждого автора и его слов из сообщений рисуем ломаную кривую
        plt.plot(
            all_lemmas.keys(),
            np.array([lemmas[l] for l in all_lemmas]),
            label=author)
    # сохраняем в файл
    plt.savefig('lemmas_by_authors.png')

    print("Finished!")