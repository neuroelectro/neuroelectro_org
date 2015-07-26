# NeuroElectro

[![Join the chat at https://gitter.im/neuroelectro/neuroelectro_org](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/neuroelectro/neuroelectro_org?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Stories in Ready](https://badge.waffle.io/neuroelectro/neuroelectro_org.png?label=ready&title=Ready)](https://waffle.io/neuroelectro/neuroelectro_org)

The aim of the **NeuroElectro Project** is to represent structured electrophysiological information from diverse neuron types. Currently, this information is obtained by text-mining and manually curating the neuroscience literature (see the [NeuroElectro Publications](http://www.neuroelectro.org/publications/) for details).

Currently this repository encapsulates the majority of the features of the project, including text-mining (located in the folder labelled "article_text_mining"), the models specifying the relational database (implemented in Django), and the website front end and back end code (implemented in Python's Django web framework).
 
Interested collaborators and contributors should contact @stripathy or @rgerkin, post in the [Gitter chat](https://gitter.im/neuroelectro/neuroelectro_org), or post to the [Google Groups Mailing List](https://groups.google.com/forum/#!forum/neuroelectro).

## Code Repository Objectives
* **Information Management**
  * Integrate and structure data related to neuron type electrophysiology, like resting membrane potentials or spike amplitudes
  * Develop and maintain APIs for accessing and downloading data
  * Keep data up-to-date
* **Text-mining**
  * Apply algorithms for downloading neuroscience articles
  * Identify electrophysiological parameters, neuron types and subtypes, and methodological information
  * Identify experimental factors like use of genetically modified animals
* **Data Curation**
  * Provide a curation interface for use by human curators to check and fix the text-mined content
* **Web Interface**
  * Provide an interactive web interface where extracted data is viewable and searchable
  * Ensure that all extracted data is trace-able back to its source

## Some use cases
  * I want to know the average value of an electrophysiological parameter in a neuron type
  * I want to find publications reporting electrophysiological data about my favorite neuron type
  * I need relistic parameters to constrain my computational model of a neuron type
  * I want to see how variable an electrophysiological property (like [resting membrane potential](http://www.neuroelectro.org/ephys_prop/3/)) is across neuron types and different publications within a neuron type.
  * I want to see how experimental parameters and metadata affect electrophysiological measurements
  * I would like to compare electrophysiological variability across neuron types with gene expression variability

  ![NeuroElectro Logo](https://raw.githubusercontent.com/neuroelectro/neuroelectro_org/master/media/images/neuroelectro.png)

