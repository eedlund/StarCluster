#!/usr/bin/env python

from starcluster import config
from starcluster import optcomplete
from starcluster.logger import log

from base import CmdBase


class CmdRemoveVolume(CmdBase):
    """
    removevolume [options] <volume_id>

    Delete one or more EBS volumes

    WARNING: This command will *permanently* remove an EBS volume.
    Please be careful!

    Example:

        $ starcluster removevolume vol-999999
    """
    names = ['removevolume', 'rv']

    @property
    def completer(self):
        if optcomplete:
            try:
                cfg = config.StarClusterConfig().load()
                ec2 = cfg.get_easy_ec2()
                completion_list = [v.id for v in ec2.get_volumes()]
                return optcomplete.ListCompleter(completion_list)
            except Exception, e:
                log.error('something went wrong fix me: %s' % e)

    def addopts(self, parser):
        parser.add_option("-c", "--confirm", dest="confirm",
                          action="store_true", default=False,
                          help="do not prompt for confirmation, just " + \
                          "remove the volume")

    def execute(self, args):
        if not args:
            self.parser.error("no volumes specified. exiting...")
        for arg in args:
            volid = arg
            ec2 = self.cfg.get_easy_ec2()
            vol = ec2.get_volume(volid)
            if vol.status in ['attaching', 'in-use']:
                log.error("volume is currently in use. aborting...")
                return
            if vol.status == 'detaching':
                log.error("volume is currently detaching. " + \
                          "please wait a few moments and try again...")
                return
            if not self.opts.confirm:
                resp = raw_input("**PERMANENTLY** delete %s (y/n)? " % volid)
                if resp not in ['y', 'Y', 'yes']:
                    log.info("Aborting...")
                    return
            if vol.delete():
                log.info("Volume %s deleted successfully" % vol.id)
            else:
                log.error("Error deleting volume %s" % vol.id)
