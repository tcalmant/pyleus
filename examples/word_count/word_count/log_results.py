import logging
import os
import tempfile

from pyleus.storm import SimpleBolt

log = logging.getLogger('log_results')


class LogResultsBolt(SimpleBolt):

    def process_tuple(self, tup):
        word, count = tup.values
        log.debug("%s: %d", word, count)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename=os.path.join(tempfile.gettempdir(),
                              'word_count_results.log'),
        format="%(message)s",
        filemode='a',
    )

    LogResultsBolt().run()
