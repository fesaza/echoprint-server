#!/usr/bin/env python
# encoding: utf-8
"""
api.py

Created by Brian Whitman on 2010-06-16.
Copyright (c) 2010 The Echo Nest Corporation. All rights reserved.
"""
from __future__ import with_statement

import web
import fp
import re

try:
    import json
except ImportError:
    import simplejson as json

# Very simple web facing API for FP dist

urls = (
    '/query', 'query',
    '/query?(.*)', 'query',
    '/ingest', 'ingest',
)


class ingest:
    def POST(self):
        params = web.input(track_id="default", fp_code="", artist=None, release=None, track=None, length=None, codever=None, source=None, genre=None, bitrate=None, sample_rate=None)
        print params
        if params.track_id == "default":
            track_id = fp.new_track_id()
        else:
            track_id = params.track_id
        if params.length is None or params.codever is None:
            return web.webapi.BadRequest()

        # First see if this is a compressed code
        if re.match('[A-Za-z\/\+\_\-]', params.fp_code) is not None:
           code_string = fp.decode_code_string(params.fp_code)
           if code_string is None:
               return json.dumps({"track_id":track_id, "ok":False, "error":"cannot decode code string %s" % params.fp_code})
        else:
            code_string = params.fp_code

        data = {"track_id": track_id,
                "fp": code_string,
                "length": params.length,
                "codever": params.codever }
        if params.artist: data["artist"] = params.artist
        if params.release: data["release"] = params.release
        if params.track: data["track"] = params.track
        if params.source: data["source"] = params.source
        if params.genre: data["genre"] = params.genre
        if params.bitrate: data["bitrate"] = params.bitrate
        if params.sample_rate: data["sample_rate"] = params.sample_rate

        fp.ingest(data, do_commit=True, local=False)

        return json.dumps({"track_id":track_id, "status":"ok"})

class query:
    def DELETE(self):
        params = web.input(track_id="")
        fp.delete(params.track_id.encode("utf-8"))

    def POST(self):
        return self.GET()

    def GET(self):
        stuff = web.input(fp_code="")
        response = fp.best_match_for_query(stuff.fp_code)
        track_info = {key: value for key, value in response.metadata.items()
                     if key != "import_date"}
        if "track_id" in track_info.keys():
            track_info["track_id"] = track_info["track_id"].split("-")[0]

        return json.dumps({"ok":True, "query":stuff.fp_code, "message":response.message(), "match":response.match(), "score":response.score, \
                         "qtime":response.qtime, "track_id":response.TRID, "total_time":response.total_time, "track_info":track_info})


application = web.application(urls, globals())#.wsgifunc()

if __name__ == "__main__":
    application.run()

