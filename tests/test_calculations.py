"""Fee calculator smoke tests."""
import json
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def calc(k, price):
    cmd=["node","-e","const m=require(process.argv[1]),f=require(process.argv[2]); console.log(JSON.stringify(m.calc(f,process.argv[3],{price:Number(process.argv[4])})))",str(ROOT/"src/calc.js"),str(ROOT/"data/fees.json"),k,str(price)]
    return json.loads(subprocess.check_output(cmd,text=True))
class Fees(unittest.TestCase):
    def test_known_fee_examples(self):
        for k,fee in [("ebay",14),("poshmark",20),("mercari",10),("depop",3.75),("etsy",9.95),("whatnot",11.2)]:
            with self.subTest(platform=k): self.assertAlmostEqual(calc(k,100)["fees"],fee,places=2)
    def test_zero(self):
        self.assertEqual(calc("ebay",0)["fees"],0)
