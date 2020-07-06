# lutxt
lutxt is a plaint lookup table format for standard cell characterization

# Format explaination
First line always donates the shape of lookup table. From the second line to the end donates the scope of lookup table 

The meaning of each column:
|      column 1  | column 2 | column 3 | column 4 |column 5 | column 6 |
|:-------|:------|:-------|:-------|:-------|:-------|
|  input slew | output load |delay(mean)|delay(stddev)|output_slew(mean)|output_slew(stddev)|

> Time unit:s  Capacitance unit:F
