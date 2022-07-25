import java.util.*;
import java.io.*;
import java.net.*;
import java.util.zip.GZIPInputStream;

public class ParserVC {
	private File resultDir;
	private File pingDir;
	private File outputFile;
	private boolean debug = true;
	private boolean dumpRawData = true;
	private String entryNode;
	private String victimIP;
	static final int numPingHosts = 2000;//Change as needed
	private Hashtable<String, Double> latencies = null;
	private HashSet<String> hosts = null;

	public ParserVC(String dirName) throws FileNotFoundException {
		resultDir = new File(dirName);
		//int a = dirName.lastIndexOf("/");
		//String dirNamePing = dirName.substring(0, a) + "/run1P-1";
		String dirNamePing = dirName;
		//pingDir = new File(dirNamePing);
		pingDir = new File(dirName);
		if (dumpRawData) outputFile = new File(dirNamePing.substring(0,dirNamePing.length()-1).replace('/','-') + ".data");
	}

	public Hashtable<String, Double> getLatencies() throws IOException, FileNotFoundException {
		if (latencies != null) return latencies;
		hosts = new HashSet<String>(10*numPingHosts);
		Hashtable<String, Double> result = new Hashtable<String, Double>(10*numPingHosts*numPingHosts);
		File[] dataFiles = pingDir.listFiles(new FilenameFilter() {
			public boolean accept(File d, String name) {
				//return name.toLowerCase().startsWith("file") && (name.indexOf(".") != -1);
				return name.toLowerCase().startsWith("filenew");
			}
		});

		PrintWriter output = null;

		if (dumpRawData) {
			outputFile.createNewFile(); //this does not actually do what you'd expect!

			output = new PrintWriter(new FileOutputStream(outputFile));

			if (debug) System.err.println("output file " + outputFile.getName());
		}

		if (debug) System.err.println("Processing " + dataFiles.length + " data files:");

		for(int i = 0; i < dataFiles.length; i++) {
			if (debug) System.err.println("reading file " + dataFiles[i].getName()); 
			BufferedReader df;
			if (dataFiles[i].getName().endsWith(".gz")) {
				df = new BufferedReader(new InputStreamReader(new GZIPInputStream(new FileInputStream(dataFiles[i]))));
			}
			else {
				df = new BufferedReader(new FileReader(dataFiles[i]));	    
			}
			Hashtable<String, Double> fromThisHostTime = new Hashtable<String, Double>(10*numPingHosts);
			Hashtable<String, Integer> fromThisHostCount = new Hashtable<String, Integer>(10*numPingHosts);
			String fromHostName = df.readLine();
			// Need to convert hostname to IP address.  Yech.
			String fromHost = "";
			try {
				fromHost = InetAddress.getByName(fromHostName).getHostAddress();
			} catch (UnknownHostException uhe) {
				fromHost = fromHostName;
			}
			if (fromHost.indexOf(":") != -1) {
				System.err.println("ParserVC: hostname " + fromHostName + " resolved to " + fromHost);
			}
			hosts.add(fromHost);
			if (debug) System.err.println("from host: " + fromHost);
			String nextLine;
			String toHost = "";
			while ((nextLine = df.readLine()) != null) {
				if (nextLine.equals("\\n")) continue;
				StringTokenizer st = new StringTokenizer(nextLine, " :");
				while (st.hasMoreTokens()) {
					String tok = st.nextToken();
					if (tok.equals("from")) {
						toHost = st.nextToken();
						hosts.add(toHost);
					}
					if (tok.startsWith("time=")) {
						double time = Double.parseDouble(tok.substring(tok.indexOf('=')+1));
						Double ft = fromThisHostTime.get(toHost);
						Integer fc = fromThisHostCount.get(toHost);
						if (ft != null) {
							time += ft.doubleValue();
						}
						fromThisHostTime.put(toHost, new Double(time));
						if (fc == null) {
							fromThisHostCount.put(toHost, new Integer(1));
						} else {
							fromThisHostCount.put(toHost, new Integer(fc.intValue()+1));
						}
					}

				}
				//		if (debug) System.err.println("to host: " + toHost);
			}
			// Finished reading one file, commit to result
			Enumeration<String> toHosts = fromThisHostTime.keys();
			double totalTime = 0;
			double squareTotalTime = 0;
			int count = 0;
			while(toHosts.hasMoreElements()) {
				String nextHost = toHosts.nextElement();
				double time = fromThisHostTime.get(nextHost).doubleValue() / fromThisHostCount.get(nextHost).intValue();
				result.put(fromHost + "|" + nextHost, new Double(time));
				if (dumpRawData) {
					if (debug) System.out.println(fromHost + ":" + nextHost + ":" + new Double(time));
					output.println(fromHost + ":" + nextHost + ":" + new Double(time));
				}
				count++;
				totalTime += time;
				squareTotalTime += time*time;
			}
			double mean = totalTime / count;
		        double stddev = Math.sqrt(squareTotalTime/count - mean*mean );
			if (debug) {
				System.out.println("Standard Deviation for file " + dataFiles[i].getName() + " for host " + fromHost + " is " + stddev);
				System.out.println("Mean for file " + dataFiles[i].getName() + " for host " + fromHost + " is " + mean);
			}
		}
		latencies = result;
		output.close();
		return result;
	}

	public HashSet<String> getHosts() throws IOException, FileNotFoundException {
		if (hosts == null) getLatencies();
		return hosts;
	}

	public String getEntryNode() throws FileNotFoundException, IOException {
		return entryNode;
	}

	public String getVictim() throws FileNotFoundException, IOException {
		return victimIP;
	}
	
	public void setEntryNode(String e) {
		entryNode = e;
	}
	
	public void setVictim(String v) {
		try {
			victimIP = InetAddress.getByName(v).getHostAddress();
		} catch (UnknownHostException uhe) {
			victimIP = v;
		}
	}

	public double getActualVictimLatency()  throws FileNotFoundException, IOException {
		if (latencies == null) getLatencies();
		return (latencies.get(getVictim() + "|" + getEntryNode())).doubleValue();
	}

	public static void main(String[] args) {
		if (args.length != 1) {
			System.out.println("One argument only, please.");
			return;
		}

		try {
			ParserVC p = new ParserVC(args[0]);
			p.debug = false;
			p.dumpRawData = false;
//			double d = p.getEstimatedVictimLatency();
//			double e = p.getActualVictimLatency();

//			System.out.println("Estimated latency victim -> entry " + d);
//			System.out.println("Actual latency victim -> entry " + e);
		} catch (Throwable t) {
			t.printStackTrace(System.err);
		} 

		return;
	}
}
