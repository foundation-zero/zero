# Introduction

This repository configures a PCanAdapter to listen on a specified IP address and port for UDP-wrapped PCan messages. It also includes a stub that periodically sends PCan messages to the same address.

# Setup

 - Create `.env` based on `.env-example`
 - `poetry install --with dev,test`
 - `poetry run python -m backend`
