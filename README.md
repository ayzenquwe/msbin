Binary XML Decoder
==================

Simple decoder for Microsoft binary XML format (MC-NBFX). Suitable for binary SOAP as well (MC-NBFS).
Basically, all this decoder does is transforming binary XML bytes into _dictionary_.

Can be used as a standalone script:
```
./msbin.py input_file
```

Example
-------
Raw input like this:
```
0000000: 5602 0b01 7304 0b01 6106 5608 440a 1e00  V...s...a.V.D...
0000010: 8299 0a75 726e 3a4d 7954 6573 7401 560e  ...urn:MyTest.V.
0000020: 4006 5265 7375 6c74 5f0a 536f 6d65 5374  @.Result_.SomeSt
0000030: 6174 7573 9902 4f4b 5f07 536f 6d65 5661  atus..OK_.SomeVa
0000040: 7285 5f05 4974 656d 7309 0101 0101       r._.Items.....
```
is transformed to human format:
```
{
  "Envelope": {
    "Body": {
      "Result": {
        "Items": null,
        "SomeStatus": "OK",
        "SomeVar": false
      }
    },
    "Header": {
      "Action": "urn:MyTest"
    }
  }
}
```
