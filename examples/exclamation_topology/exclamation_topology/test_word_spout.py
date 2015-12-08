from __future__ import absolute_import

import logging

import random
import time
import os
import tempfile

from pyleus.storm import Spout


log = logging.getLogger('test_word_spout')


class TestWordSpout(Spout):

    WORDS = ["ben", "patrick", "antonio", "michael", "jeremy", "darwin"]

    OUTPUT_FIELDS = ["word"]

    def next_tuple(self):
        time.sleep(0.5)
        word = random.choice(self.WORDS)
        log.debug(word)
        self.emit((word,))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename=os.path.join(tempfile.gettempdir(),
                              'exclamation_spout.log'),
        filemode='a',
    )

    TestWordSpout().run()
