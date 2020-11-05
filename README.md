# Veides Agent SDK for Python

[![Build Status](https://travis-ci.org/Veides/veides-agent-sdk-python.svg?branch=master)](https://travis-ci.org/Veides/veides-agent-sdk-python)
[![Coverage Status](https://coveralls.io/repos/github/Veides/veides-agent-sdk-python/badge.svg?branch=master)](https://coveralls.io/github/Veides/veides-agent-sdk-python?branch=master)

This repository contains Python module for Veides Agent SDK. It allows Python developers to easily connect agents and interact with Veides platform. 

**Jump to**:

* [Installation](#Installation)
* [Samples](#Samples)
* [Features](#Features)

## Installation

### Using pip

```bash
pip install veides-agent-sdk
```

### From source

```bash
git clone https://github.com/Veides/veides-agent-sdk-python.git
python3 -m pip install ./veides-agent-sdk-python
```

## Samples

[Samples README](https://github.com/Veides/veides-agent-sdk-python/blob/master/samples)

## Features

- **SSL/TLS**: By default, this library uses encrypted connection
- **Auto Reconnection**: Client support automatic reconnect to Veides in case of a network issue
