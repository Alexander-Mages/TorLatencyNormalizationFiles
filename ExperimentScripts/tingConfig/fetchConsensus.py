from stem.descriptor import DocumentHandler
from stem.descriptor.remote import DescriptorDownloader

downloader = DescriptorDownloader()
consensus = downloader.get_consensus(document_handler = DocumentHandler.DOCUMENT).run()[0]

with open('/users/magesap/TorLatencyNormalizationFiles/ExperimentScripts/tingOnDeter/ting/tor/data/w/cached-consensus', "w") as cachedConsensus:
       cachedConsensus.write(str(consensus))

#with open('/home/alex/cachedConsensus', "w") as cachedConsensus:
#	cachedConsensus.write(str(consensus))
