# -*- coding: utf-8 -*-
"""ЛР №4, вариант 16. Запуск «Генераторной станции»."""

import sys

from genlab.cli import main


if __name__ == "__main__":
    # защита нужна для ProcessPoolExecutor на Windows
    sys.exit(main())
