#!/bin/sh

http --verbose POST localhost:5000/games/new/ @"$1"
