#!/bin/bash

declare fgt_1="10.200.6.100"
declare fgt_2="10.200.6.101"
declare pass="toremove"

./reset.except ${fgt_1} ${pass}
./reset.except ${fgt_2} ${pass}

./factory_reset.except ${fgt_1}
./factory_reset.except ${fgt_2}