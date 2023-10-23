
import logging
from os import listdir
from os.path import join
from typing import Tuple, NewType, Dict, Set
from collections import defaultdict

from annotations import Annotations


DocumentId = NewType('DocumentId', str)
FileNumber = NewType('FileNumber', str)
TextDict = NewType('TextDict', Dict[DocumentId, Dict[FileNumber, str]])
AnnDict = NewType('AnnDict', Dict[DocumentId, Dict[FileNumber, Annotations]])


class DataLoader:

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def  _load_txt_file(self, doc_dir: str, file_name: str) -> Tuple[str, str]:
        """
        Load contents of text file and return file number + content. Naming
        convention for gold set files is <doc_id>_<file_number>.<txt/ann> -- 
        every document is split into files of 100 sentences each, `file_number`
        indicates the ordering of these split files.

        :param doc_dir: _description_
        :type doc_dir: str
        :param file_name: _description_
        :type file_name: str
        :return: _description_
        :rtype: Tuple[str, str]
        """
        fnum = file_name.replace('.txt', '').split('_')[-1]
        with open(join(doc_dir, file_name)) as f_in:
            return fnum, f_in.read()

    def _load_ann_file(
            self, doc_dir: str, file_name: str
    ) -> Tuple[str, Annotations]:
        """
        _summary_

        :param doc_dir: _description_
        :type doc_dir: str
        :param file_name: _description_
        :type file_name: str
        :return: _description_
        :rtype: Tuple[str, Annotations]
        """
        fnum = file_name.replace('.ann', '').split('_')[-1]
        fnum = fnum.replace('.txt', '')
        doc_ann = Annotations()
        with open(join(doc_dir, file_name)) as f_in:
            for row in f_in.readlines():
                try:
                    doc_ann.add_annotation(row.strip('\n'))
                except ValueError:
                    self._logger.warning(
                        'Invalid annotation: %s', row.strip('\n')
                    )
        return fnum, doc_ann

    def load_annotations(
            self, ann_dir: str, donot_list: Set[str] = None,
            sem_types: Set[str] = None
    ) -> Tuple[TextDict, AnnDict]:
        """
        _summary_

        :param ann_dir: _description_
        :type ann_dir: str
        :param donot_list: set of IMUIs to be removed
        :type donot_list: Set[str]
        :param sem_types: only keep these semantic categories
        :type sem_types: Set[str]
        :return: _description_
        :rtype: Tuple[TextDict, AnnDict]
        """

        text = defaultdict(dict)
        ann = defaultdict(dict)

        self._logger.info('Loading annotations from %s', ann_dir)

        for document in listdir(ann_dir):
            if document.startswith('.') or document.endswith('.txt'):
                continue
            if document.endswith('.csv'):
                continue
            doc_dir = join(ann_dir, document)
            for file in sorted(listdir(doc_dir)):
                if file.endswith('.txt'):
                    fnum, content = self._load_txt_file(doc_dir, file)
                    text[document][fnum] = content
                if file.endswith('.ann'):
                    fnum, doc_ann = self._load_ann_file(doc_dir, file)
                    if donot_list is not None:
                        self._logger.info('Filtering %s by donot list', file)
                        self._logger.info(
                            '%d annotations before filtering', len(doc_ann)
                        )
                        doc_ann = doc_ann.filter_by_donot_list(donot_list)
                        self._logger.info(
                            '%d annotations after filtering', len(doc_ann)
                        )
                    if sem_types is not None:
                        self._logger.info('Filtering by type')
                        self._logger.info(
                            '%d annotations before filtering', len(doc_ann)
                        )
                        doc_ann = doc_ann.filter_by_types(sem_types)
                        self._logger.info(
                            '%d annotations after filtering', len(doc_ann)
                        )
                    ann[document][fnum] = doc_ann

        total = sum([len(ann[d][fn]) for d in ann for fn in ann[d]])
        self._logger.info('Loaded %d annotations', total)
        
        return text, ann
