import java.util.*;
import java.io.*;

class VecVC {
	Vector<Double> v;

	public VecVC(int size) {
		v = new Vector<Double>(size);
	}

	public VecVC(Vector<Double> a) {
		v = a;
	}

	public int size() {
		return v.size();
	}

	public Double get(int i) {
		return v.get(i);
	}

	public void set(int i, Double x) {
		v.add(i, x);
	}

	public void set(int i, double x) {
		set(i, new Double(x));
	}

	//all of the following manipulation functions return a new Vec; no mutators

	public VecVC add(VecVC y) {
		if (v.size() != y.size()) {
			System.err.println("Vec size mismatch!");
			System.exit(1);
		}
		if (v.size() != y.size()) {
			System.err.println("Vec capacity mismatch!");
			System.exit(1);
		}
		VecVC result = new VecVC(v.size());
		for(int i = 0; i < v.size(); i++) {
			result.set(i, v.get(i) + y.get(i));
		}
		return result;
	}

	public VecVC scale(double a) {
		VecVC result = new VecVC(v.size());
		for(int i = 0; i < v.size(); i++) {
			result.set(i, v.get(i) * a);
		}
		return result;
	}

	public double len() {
		double sum = 0;
		for(int i = 0; i < v.size(); i++) {
			sum += v.get(i) * v.get(i);
		}
		double result = Math.sqrt(sum);
		if (Double.isNaN(result)) {
			System.err.println("Found NaN length in " + this.toString());
			System.exit(3);
		}
		return java.lang.Math.sqrt(sum);
	}

	public double dist(VecVC y) {
		if (y == null) {
			System.err.println("Cannot compute distance to null value");
			System.exit(2);
			//return 0;
		}
		return this.add(y.scale(-1)).len();
	}

	public String toString() {
		String out = new String("<");
		for(int i = 0; i < v.size(); i++) {
			out += v.get(i);
			if (!(i == v.size())) out += " ";
		}
		out += ">";
		return out;
	}
}

public class ProcessVC {
	static HashSet<String> hosts;
	static Hashtable<String,Double> latency;
	static ParserVC p;
	static Hashtable<String,VecVC> pos = new Hashtable<String,VecVC>();
	static Random rand = new Random();
	static double E;

/*
//reading inputs
	static void read_pings(String arg) throws java.io.FileNotFoundException, java.io.IOException {
 	BufferedReader in = new BufferedReader(new FileReader(arg));
// System.out.println("Reading " + argv[0])";
		String host = in.readLine(); //already chomped
// System.out.println(host)";
		hosts.add(host);
		String nextline;
		while((nextline = in.readLine()) != null) {
			String[] tuple = nextline.split("\\s+");
			String dest = tuple[0];
			double dist = Double.parseDouble(tuple[1]);
			if (dist == 0) continue;
			//else
			latency.put(host + "|" + dest, new Double(dist));
			latency.put(dest + "|" + host, new Double(dist));
			hosts.add(dest);
			System.out.print(".");
//   System.out.println("Inserted latency " + host + " -> " + dest + " " + dist");
		}
		in.close();
		System.out.println("");
	}
	*/
	//Parser2.getLatencies() gives me latencies hashtable

	static void init_coords() {
		Iterator<String> i = hosts.iterator();
		while(i.hasNext()) {
			VecVC coord = new VecVC(4);
			coord.set(0, rand.nextInt(200));
			coord.set(1, rand.nextInt(200));
			coord.set(2, rand.nextInt(200));
			coord.set(3, rand.nextInt(200));
			pos.put(i.next(), coord);
			//System.out.print(".");
		}
		//System.out.println("");
	}

	/* static String match_victims_lans(HashSet<String> victims, HashSet<String> lans) {
		String close_lan = new String();
		Iterator<String> i = victims.iterator();
		for(String victim = i.next(); i.hasNext(); victim = i.next()) {
			double min_dist = 1000000;
			System.out.println("Distances from " + victim + " to:");
			Iterator<String> j = lans.iterator();
			for (String lan = j.next(); j.hasNext(); lan = j.next()) {
				System.out.print("\t" + lan + ":");
				double cdist = pos.get(lan).dist(pos.get(victim));
				System.out.println(cdist);
				if (cdist < min_dist) {
					min_dist = cdist;
					close_lan = lan;
				}
			}
			System.out.println("\t" + victim + "is closest to " + close_lan + ", distance " + min_dist);
		}
		return close_lan;
	} */

	static double error() {
	    double err = 0;
	    double sum = 0;
	    int count = 0;
	    Set<String> s = latency.keySet();
	    Iterator<String> it = s.iterator();
	    while (it.hasNext()) {
		String key = it.next();
		String[] tuple = key.split("\\|");
		String h1 = tuple[0];
		String h2 = tuple[1];
		//System.out.println(h1);
		//System.out.println(h2);
		if (pos.get(h1) == null) System.err.println("get h1 failed");
		if (pos.get(h2) == null) System.err.println("get h2 failed");
		if (latency.get(h1 + "|" + h2) == null) System.err.println("get h1|h2 failed");
		double dist = latency.get(h1 + "|" + h2) - pos.get(h1).dist(pos.get(h2));
		err += dist * dist;
		count++;
		sum += java.lang.Math.abs(dist);
	    }
	    //	    System.out.println("average absolute error = " + sum / count);
	    return err/count;
	}
    
    static void find_coordinates() {
	double err = error();
	double new_err = err - 1000;
	for(int a = 0 ; a < 200; a++) {
	    err = new_err;
	    if (a % 10 == 0) System.err.println("Error now " + err);
	    Iterator<String> i = hosts.iterator();
	    for(String host = i.next(); i.hasNext(); host = i.next()) {
		VecVC f = new VecVC(4);
		f.set(0, 0);
		f.set(1, 0);
		f.set(2, 0);
		f.set(3, 0);

		Iterator<String> i2 = hosts.iterator();
		for (String dest = i2.next(); i2.hasNext(); dest = i2.next()) {
		    if (host.equals(dest)) continue;
		    Double d = latency.get(host + "|" + dest);
		    if (d == null) {
			Double dd = latency.get(dest + "|" + host);
			if (dd == null) continue;
			else d = dd;
		    } 
		    VecVC delta = pos.get(host).add(pos.get(dest).scale(-1));
		    double dist = delta.len();
		    double e = d.doubleValue() - dist;
		    f = f.add(delta.scale(e/dist));
		}
		//pos.put(host, pos.get(host).add(f.scale(0.004)));
		pos.put(host, pos.get(host).add(f.scale(0.002)));
	    }
	    new_err = error();
	    System.err.println("New error is " + new_err);
	    //System.out.println("");
	}
    }
    
	public static void main(String[] args) throws java.io.FileNotFoundException, java.io.IOException {
		if (args.length != 3) {
			System.out.println("Need 3 args - directory path and filename of victims and filename of pinged hosts");
			System.exit(1);
		}

		p = new ParserVC(args[0]);
		latency = p.getLatencies();
		hosts = p.getHosts();

		init_coords();

		System.err.println("Before find_coordinate");
		find_coordinates();
		System.err.println("After find_coordinates");

		BufferedReader victims = new BufferedReader(new FileReader(args[1]));
		String nextLineV;
		
		while ( (nextLineV = victims.readLine()) != null) {
			BufferedReader pings = new BufferedReader(new FileReader(args[2]));
			String nextLineP;
			while ( (nextLineP = pings.readLine()) != null) {
				p.setVictim(nextLineV);
				p.setEntryNode(nextLineP);
				boolean canContinue = true;
					
				if (latency.get(nextLineV + "|" + nextLineP) != null) {
					double distance = latency.get(nextLineV + "|" + nextLineP);
					System.out.println("Ping distance from " + nextLineV + " to node " + p.getEntryNode() + " is " + distance);
				}
				
			/*	VecVC pinger = pos.get(nextLineV);
				VecVC pingee = pos.get(nextLineP);
				
				if (pinger != null) {
					if (pingee != null) {
						double distance = pinger.dist(pingee);
						System.out.println("Coordinate distance from " + nextLineV + " to node " + p.getEntryNode() + " is " + distance);
					} else {
						System.err.println("pingee is null - " + nextLineV + " and " + nextLineP);
					}
				} else {
					if (pingee != null) {
						System.err.println("pinger is null - " + nextLineV + " and " + nextLineP);
					} else {
						System.err.println("pingee and pinger are null - " + nextLineV + " and " + nextLineP);
					}
				}
			*/	
				
				/*Hashtable<String,Double> distances = new Hashtable<String,Double>();

				//sort hosts lists by distance from entry node (coordinates)
				Iterator<String> it = hosts.iterator();
				for(String victim = it.next(); it.hasNext(); victim = it.next()) {
					String en = p.getEntryNode();
					//String victim = p.getVictim();
					//System.err.println("Entry node: "+en);
					VecVC posVec = pos.get(en);
					if (posVec == null) {
						canContinue = false;
					} else {
						//System.err.println("Position vector: "+posVec.toString());
						distances.put(victim, new Double(pos.get(victim).dist(posVec)));
					}
				}*/

		//			Hashtable<String,Double> sorter = new Hashtable<String,Double>();

				//double victimLatency = p.getEstimatedVictimLatency();
				//System.out.println("Guess is: " + victimLatency);
				//now sort by distance from victim latency
		//			Set<String> s = distances.keySet();
		//			String[] a = new String[2];
		//			a = s.toArray(a);
		//			for (int j=0; j < s.size(); j++) {
		//				if ((1-E)*victimLatency <= distances.get(a[j]).doubleValue() && (1+E)*victimLatency > distances.get(a[j]).doubleValue())
		//				System.out.println("Host " + a[j] + ":" + distances.get(a[j]));
					//sorter.put(a[j], distances.get(a[j]));
		//			}

				/*if (canContinue) {
					String victim = p.getVictim();
				//System.out.println("Our lucky victim is: " + victim);
				//System.out.println("Guess is: " + victimLatency);
					System.out.println("Coordinate distance from " + victim + " to node " + p.getEntryNode() + " is " + distances.get(victim));
				}*/
			}
		}
	}
}
