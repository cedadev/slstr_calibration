#!/bin/sh

/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/make_mpc_level0_config.sh S3A

/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_level0_S3A.cfg -v  -Ce >/dev/null 2>&1
