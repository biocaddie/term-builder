#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BioCADDIE Terminology Utilities
UMLS Semantic Types

Created on   : 2015-07-09 ( Ergin Soysal )
Last modified: Aug 07, 2015, Fri 20:42:55 -0500
"""

SEM_TYPES = {
    'morg': [
        'T007',    # Bacterium
        'T194',    # Archaeon
        'T004',    # Fungus
        'T005',    # Virus
    ],
    'org': [
        'T008',    # Animal
        'T204',    # Eukaryote
        'T012',    # Bird
        'T011',    # Amphibian
        'T013',    # Fish
        'T016',    # Human
        'T015',    # Mammal
        'T032',    # Organism Attribute
        'T040',    # Organism Function
        'T001',    # Organism
        'T002',    # Plant
        'T014',    # Reptile
        'T010',    # Vertebrate
    ],
    'chem': [
        'T103',    # Chemical
        'T120',    # Chemical Viewed Functionally
        'T104',    # Chemical Viewed Structurally
        'T197',    # Inorganic Chemical
        'T196',    # Element, Ion, or Isotope
        'T109',    # Organic Chemical
        'T118',    # Carbohydrate
        'T088',    # Carbohydrate Sequence
        'T119',    # Lipid
        'T127',    # Vitamin
        'T111',    # Eicosanoid
        'T124',    # Neuroreactive Substance or Biogenic Amine
        'T125',    # Hormone
        'T110',    # Steroid
        'T115',    # Organophosphorus Compound
        'T131',    # Hazardous or Poisonous Substance
    ],
    'subs': [
        'T167',    # Substance
        'T031',    # Body Substance
        'T122',    # Biomedical or Dental Material
        'T123',    # Biologically Active Substance
    ],
    'med': [
        'T200',    # Clinical Drug
        'T195',    # Antibiotic
        'T121',    # Pharmacologic Substance
    ],
    'thrp': [
        'T061',    # Therapeutic or Preventive Procedure
        'T058',    # Health Care Activity
    ],
    'prot': [
        'T116',    # Amino Acid, Peptide, or Protein
        'T087',    # Amino Acid Sequence
        'T126',    # Enzyme
    ],
    'body': [
        'T190',    # Anatomical Abnormality
        'T017',    # Anatomical Structure
        'T022',    # Body System
        'T029',    # Body Location or Region
        'T023',    # Body Part, Organ, or Organ Component
        'T030',    # Body Space or Junction
        'T019',    # Congenital Abnormality
        'T018',    # Embryonic Structure
        'T082',    # Spatial Concept
        'T024',    # Tissue
        'T021',    # Fully Formed Anatomical Structure
        # cell
        'T026',    # Cell Component
        'T025',    # Cell
    ],
    'prob': [
        'T020',    # Acquired Abnormality
        'T049',    # Cell or Molecular Dysfunction
        'T047',    # Disease or Syndrome
        'T033',    # Finding
        'T191',    # Neoplastic Process
        'T046',    # Pathologic Function
        'T184',    # Sign or Symptom
        'T037',    # Injury or Poisoning
        'T048',    # Mental or Behavioral Dysfunction
    ],
    'lab': [
        'T060',    # Diagnostic Procedure
        'T059',    # Laboratory Procedure
        'T034',    # Laboratory or Test Result
        'T130',    # Indicator, Reagent, or Diagnostic Aid
    ],
    'gene': [
        'T045',    # Genetic Function
        'T028',    # Gene or Genome
        'T114',    # Nucleic Acid, Nucleoside, or Nucleotide
        'T086',    # Nucleotide Sequence
        'T044',    # Molecular Function
        'T085',    # Molecular Sequence
        'T043',    # Cell Function
    ],
    'other': [
        'T100',    # Age Group

        # body funct
        'T053',    # Behavior
        'T038',    # Biologic Function
        'T169',    # Functional Concept
        'T041',    # Mental Process
        'T039',    # Physiologic Function
        'T042',    # Organ or Tissue Function

        'T185',    # Classification
        'T201',    # Clinical Attribute
        'T077',    # Conceptual Entity
        'T056',    # Daily or Recreational Activity
        'T065',    # Educational Activity
        'T069',    # Environmental Effect of Humans
        'T050',    # Experimental Model of Disease
        'T051',    # Event
        'T102',    # Group Attribute
        'T068',    # Human-caused Phenomenon or Process
        'T078',    # Idea or Concept
        'T129',    # Immunologic Factor
        'T055',    # Individual Behavior
        'T171',    # Language
        'T063',    # Molecular Biology Research Technique
        'T070',    # Natural Phenomenon or Process
        'T067',    # Phenomenon or Process
        'T080',    # Qualitative Concept
        'T081',    # Quantitative Concept
        'T192',    # Receptor
        'T089',    # Regulation or Law
        'T079',    # Temporal Concept

        'T083',    # Geographic Area

        'T168',    # Food

        'T090',    # Occupation or Discipline
        'T091',    # Biomedical Occupation or Discipline
        # Activity
        'T052',    # Activity
        'T066',    # Machine Activity
        'T062',    # Research Activity
        'T054',    # Social Behavior
        'T057',    # Occupational Activity
        'T064',    # Governmental or Regulatory Activity
        # entity
        'T071',    # Entity
        'T170',    # Intellectual Product
        'T073',    # Manufactured Object
        'T072',    # Physical Object
        'T074',    # Medical Device
        'T203',    # Drug Delivery Device
        'T075',    # Research Device

        'T092',    # Organization
        'T093',    # Health Care Related Organization
        'T095',    # Self-help or Relief Organization

        'T096',    # Group
        'T099',    # Family Group
        'T101',    # Patient or Disabled Group
        'T098',    # Population Group
        'T097',    # Professional or Occupational Group
        'T094',    # Professional Society
    ],
}

INV_SEM_TYPES = {}


def invertSemTypes(SEM_TYPES):
    for type in SEM_TYPES:
        for sty in SEM_TYPES[type]:
            if sty in INV_SEM_TYPES:
                print "ERROR:", sty
                exit()
            INV_SEM_TYPES[sty] = type

invertSemTypes(SEM_TYPES)

if __name__ == '__main__':
    print INV_SEM_TYPES
