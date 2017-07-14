## The stabilization phase


### SPPAS-1.8.0 (2016, 30th August)

GUI:

- Design fully revisited and tested under Linux Mint, Windows 10 and MacOS 10.9

Development:

- SLM package created: can estimate a statistical language model (without 
  smooth method) on a small corpus

Automatic annotations:

- Add a diagnosis of files
- Tokenize extended: applied also on alternative labels
- Phonetize extended: applied also on alternative labels
- Alignment code cleaning and partly re-implemented
- Add "Chunk alignment"
- Use of a .ini file to configure each annotation instead of a sppas.conf file


### SPPAS-1.8.1 (2016, 28th November)

A few tutorials are available on the web site.

Automatic annotations:

- Align: an ActivityDuration tier can be optionally added.
- Support of 3-columns tab-delimited files with .txt extension. It allows the
  compatibility with Audacity Label track files.
- Acoustic models training validated.

Resources:

- Catalan: new pronunciation dictionary and new acoustic model.


### SPPAS-1.8.2 (2017, 18th January)

Analysis:

- debug of DataFilter

Resources:

- French vocabulary and dictionary updated

Development:

- new plugins package with a new plugin manager
- GUI integration of this new plugins system
- some unittest appended and all existing ones updated
- annotationdata.io renamed annotationdata.aio
- docstrings of some packages converted from epytext to reST syntax

GUI: 

- DataStats, DataFilter and DataRoamer toolbars don't scroll anymore
- Themes management changed.
- Main font is managed by the Themes.


### SPPAS-1.8.3 (2017, 10th March)

Development:

- Elan reader highly improved (faster reader).
- updated plugins


### SPPAS 1.8.4 (2017, 10th April)

Development:

- Elan writer modified: create a time slot for each localization.


### SPPAS 1.8.5 (2017, 20th April)

Development:

- Vizualizer renamed Visualizer
- AudioRoamer: bug with an icon corrected
- New Phonedit mrk format support.
- Updated AnnotationPro Antx reader/writer


### SPPAS 1.8.6 (2017, 19th June)

Resources:

- Polish dictionary and acoustic model updated.


### SPPAS 1.9 (2017, 16th August)

Development:

- Relative imports used in the standard way for Python
- PEP 8 code style (except for wxgui)
- PEP 257 reST code documentation style (except for wxqui)
- Unittests:

      - existing tests verified, improved, extended
      - new tests added
      - tests migrated into the packages
      
- Compatibility for both Python 2.7 and Python > 3.2:

    - makeunicode.py contains functions and classes to deal with strings
    - utils, term, structs, resources, presenters, plugins, calculus packages:
      migration is done
      
- Exceptions are separately managed
- introduction of a system for the internationalization of the messages. Done
  in English and French for the packages: audiodata, calculus, plugins, 
  resources, structs, term, utils
- Package re-organization:

    - new package "models", with acm and slm
    - utils 
    - resources
    
- meta.py is replacing sp_glob.py
- new scripts: tieraligntophon.py, dictmerge.py
- Robustness to read malformed HTK-ASCII pronunciation dictionaries.
- Bug corrected in the management of pronunciation variants

Resources: 

- Add support of Naija language (pcm)
- English-French mapping table updated

Annotations:

- Tokenizer renamed into Text Normalization:

    - re-structured package
    - debug: mainly for English language, and punctuations
    - new option: output a customized tier.
    
- Repetitions:

    - re-structured package
    - debug
  
Communication:

- Add a description document of the orthographic transcription convention
  in the package.
- Web page updated, new tutorials available
- Documentation updated