"""
Classes for representing brat annotations. The brat annotation format is
described here: https://brat.nlplab.org/standoff.html
"""

from __future__ import annotations

import re
from typing import Dict, Generator, Set
from collections import defaultdict
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class AnnotationNote:
    """
    Representation of a note annotation.
    """
    note_id: str
    note_type: str
    note_ref: str
    text: str
        
    @staticmethod
    def from_string(ann: str) -> AnnotationNote:
        """
        Create AnnotationNote from a note annotation row. Expects the input
        row is formatted in the following way:

        `#1	AnnotatorNotes T1	this annotation is suspect`

        #1 -- ID
        AnnotatorNotes -- Note type
        T1 -- Referenced annotation
        this annotation is suspect -- text of the note

        :param ann: _description_
        :type ann: str
        :return: _description_
        :rtype: AnnotationNote
        """
        parts = ann.split('\t')
        if len(parts) > 3:
            note_id, note_type, note_ref, text = parts
        else:
            note_id, type_ref, text = ann.split('\t')
            note_type, note_ref = type_ref.split()
        return AnnotationNote(note_id, note_type, note_ref, text)


@dataclass
class Normalization:
    """
    Representation of a normalization annotation.
    """
    norm: str
    norm_id: str = None
    norm_ref: str = None
    name: str = None

    @staticmethod
    def from_string(ann: str) -> Normalization:
        """
        Create Normalization from a normalization annotation row. Expects the 
        input row is formatted in the following way:

        `N1	Reference T1 Wikipedia:534366	Barack Obama`

        N1 -- ID
        Reference -- Annotation type
        T1 -- Referenced annotation
        Wikipedia:534366 -- RID:EID pair identifying the external resource 
                            (RID) and the entry within that resource (EID)
        Barack Obama -- External entry reference

        :param ann: _description_
        :type ann: str
        :return: _description_
        :rtype: Normalization
        """
        cleaned = re.sub(r'[\t]+', '\t', ann)
        parts = cleaned.split('\t')
        if len(parts) == 4:
            norm_id, _, norm_ref, norm = parts
            name = None
        else:
            norm_id, ref_norm, name = parts[0], parts[1], None
            if len(parts) == 3:
                name = parts[2]
            _, norm_ref, norm = ref_norm.split()
        return Normalization(norm, norm_id, norm_ref, name)
        

@dataclass
class EntityAnnotation:
    """
    Representation of an entity annotation.
    """
    ann_id: str
    start: int
    end: int
    text: str
    ann_type: str = None
    note: AnnotationNote = None
    norm: Normalization = None
        
    @staticmethod
    def from_string(ann: str) -> Generator[EntityAnnotation]:
        """
        Create EntityAnnotation from an entity annotation row. Expects the 
        input row is formatted in the following way:

        `T1	Organization 0 4	Sony`

        T1 -- ID
        Organization -- Entity type
        0 -- Start of the entity mention in the input text
        4 -- End of the entity mention in the input text
        Sony -- Entity mention

        :param ann: _description_
        :type ann: str
        :return: _description_
        :rtype: EntityAnnotation
        """
        parts = ann.split('\t')
        if len(parts) > 3:
            ann_id, ann_type, start, end, text = parts
        else:
            ann_id, type_span, text = ann.split('\t')
            ann_type, coords = type_span.split(' ', maxsplit=1)
            for idx, coord_part in enumerate(coords.split(';')):
                start, end = coord_part.split()
                ann_id = f'{ann_id}-{idx}'
        yield EntityAnnotation(ann_id, int(start), int(end), text, ann_type)


@dataclass
class Annotations:
    """
    Class for maintaining a dictionary of {annotation_id: annotation}
    """
    annotations: Dict[str, EntityAnnotation] = field(default_factory=dict)
    id_map: defaultdict[list] = field(default_factory=lambda: defaultdict(list))
        
    def __len__(self) -> int:
        return len(self.annotations)
        
    def ann_type(self, ann_str: str) -> str:
        """
        Return annotation type from an input annotation row.

        :param ann_str: _description_
        :type ann_str: str
        :return: _description_
        :rtype: str
        """
        return ann_str.strip()[0]
        
    def add_annotation(self, ann_str: str):
        """
        Add a new annotation from an input row.

        :param ann_str: _description_
        :type ann_str: str
        :raises ValueError: _description_
        :raises ValueError: _description_
        """
        if len(ann_str.strip()) == 0:
            return
        ann_type = self.ann_type(ann_str)
        if ann_type == 'T':
            for ann in EntityAnnotation.from_string(ann_str):
                if ann.ann_id in self.annotations:
                    raise ValueError('Entity annotation ID already exists')
                self.id_map[ann.ann_id.split('-')[0]].append(ann.ann_id)
                self.annotations[ann.ann_id] = ann
        elif ann_type == '#':
            note = AnnotationNote.from_string(ann_str)
            for ann_id in self.id_map[note.note_ref]:
                self.annotations[ann_id].note = note
        elif ann_type == 'N':
            norm = Normalization.from_string(ann_str)
            for ann_id in self.id_map[norm.norm_ref]:
                self.annotations[ann_id].norm = norm
        else:
            raise ValueError(f'Unsupported annotation type: {ann_type}')
    
    def filter_by_type(self, entity_type: str) -> Annotations:
        """
        Filter annotations to a specific entity type.

        :param ann_type: _description_
        :type ann_type: str
        :return: _description_
        :rtype: Annotations
        """
        annotations = {}
        for ann in self.annotations.values():
            if ann.ann_type == entity_type:
                annotations[ann.ann_id] = ann
        return Annotations(annotations)
    
    def filter_by_types(self, entity_types: Set[str]) -> Annotations:
        """
        _summary_

        :param entity_types: _description_
        :type entity_types: Set[str]
        :return: _description_
        :rtype: Annotations
        """
        annotations = {}
        for ann in self.annotations.values():
            if ann.ann_type in entity_types:
                annotations[ann.ann_id] = ann
        return Annotations(annotations)
    
    def filter_by_offset(self, start: int, end: int) -> Annotations:
        """
        _summary_

        :param start: _description_
        :type start: int
        :param end: _description_
        :type end: int
        :return: _description_
        :rtype: Annotations
        """
        annotations = {}
        for ann in self.annotations.values():
            if ann.start >= start and ann.end <= end:
                annotations[ann.ann_id] = ann
        return Annotations(annotations)

    def filter_by_donot_list(self, donot_list: Set[str]) -> Annotations:
        """
        _summary_

        :param donot_list: _description_
        :type donot_list: Set[str]
        :return: _description_
        :rtype: Annotations
        """
        annotations = {}
        for ann in self.annotations.values():
            if ann.norm is not None:
                imui = ann.norm.norm.replace('emmet:', '')
                if imui not in donot_list:
                    annotations[ann.ann_id] = ann
            else:
                annotations[ann.ann_id] = ann
        return Annotations(annotations)

    def to_pandas(self, doc_id: str, part: str) -> pd.DataFrame:
        """
        _summary_

        :param doc_id: _description_
        :type doc_id: str
        :param part: _description_
        :type part: str
        :return: _description_
        :rtype: pd.DataFrame
        """
        data = []
        for ann in self.annotations.values():
            data.append({
                'doc_id': doc_id,
                'part': part,
                'ann_id': ann.ann_id,
                'start': ann.start,
                'end': ann.end,
                'text': ann.text,
                'imui': ann.norm.norm.split(':')[-1]
            })
        return pd.DataFrame(data)
