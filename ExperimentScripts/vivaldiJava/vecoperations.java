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
    public static void main(String[] args) {
        VecVC f = new VecVC(4);
        f.set(0,59.54780098);
        f.set(1,13.16605305);
        f.set(2,348.94968233);
        f.set(3,237.63104561);
        
        VecVC z = new VecVC(4);
        z.set(0,299.06880664);
        z.set(1,212.71267395);
        z.set(2,320.7409525);
        z.set(3,219.40839175);
        System.err.println(f.dist(z));
    }
}
