from stem.descriptor import DocumentHandler
from stem.descriptor.remote import DescriptorDownloader

downloader = DescriptorDownloader()
consensus = downloader.get_consensus(document_handler = DocumentHandler.DOCUMENT).run()[0]

with open('/home/alex/cachedConsensus', "w") as cachedConsensus:
	cachedConsensus.write(str(consensus))
