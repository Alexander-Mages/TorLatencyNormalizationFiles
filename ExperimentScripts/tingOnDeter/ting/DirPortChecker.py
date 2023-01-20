import stem.descriptor.remote
dir_port = ('206.117.25.79', 10004)
stem.descriptor.remote.Query(resource='/tor/server/authority.z', endpoints=[dir_port]).run()[0]


