#!/usr/bin/python

from rtslib import FileIOStorageObject, BlockStorageObject

from rtslib import FabricModule, Target, TPG

from rtslib import NetworkPortal, NodeACL, LUN, MappedLUN

from rtslib import RTSRoot

from rtslib import RTSLibError, RTSLibBrokenLink

from rtslib.utils import fread, fwrite, RTSLibError, generate_wwn

from rtslib.utils import is_dev_in_use, get_blockdev_type, get_blockdev_size

from rtslib.utils import convert_scsi_path_to_hctl, convert_scsi_hctl_to_path

from rtslib.tcm import so_mapping, StorageObject

from rtslib.utils import RTSLibError, RTSLibBrokenLink, RTSLibNotInCFS, modprobe, mount_configfs

from rtslib.utils import dict_remove, set_attributes

from rtslib.node import CFSNode

from configshell import ExecutionError

from ctypes import *  

import rtslib

import rtslib.root as root

import os

import stat


# def human_to_bytes(hsize, kilo=1024):
#     '''
#     This function converts human-readable amounts of bytes to bytes.
#     It understands the following units :
#         - I{B} or no unit present for Bytes
#         - I{k}, I{K}, I{kB}, I{KB} for kB (kilobytes)
#         - I{m}, I{M}, I{mB}, I{MB} for MB (megabytes)
#         - I{g}, I{G}, I{gB}, I{GB} for GB (gigabytes)
#         - I{t}, I{T}, I{tB}, I{TB} for TB (terabytes)

#     Note: The definition of I{kilo} defaults to 1kB = 1024Bytes.
#     Strictly speaking, those should not be called I{kB} but I{kiB}.
#     You can override that with the optional kilo parameter.

#     @param hsize: The human-readable version of the Bytes amount to convert
#     @type hsize: string or int
#     @param kilo: Optional base for the kilo prefix
#     @type kilo: int
#     @return: An int representing the human-readable string converted to bytes
#     '''
#     size = hsize.replace('i', '')
#     size = size.lower()
#     if not re.match("^[0-9]+[k|m|g|t]?[b]?$", size):
#         raise RTSLibError("Cannot interpret size, wrong format: %s" % hsize)

#     size = size.rstrip('ib')

#     units = ['k', 'm', 'g', 't']
#     try:
#         power = units.index(size[-1]) + 1
#     except ValueError:
#         power = 0
#         size = int(size)
#     else:
#         size = int(size[:-1])

#     return size * (int(kilo) ** power)

def create_backstore(plugin, diskname, backing_device, filesize):
	try:

		if plugin == 1:
			if os.path.isfile(backing_device):
				if filesize > 17592186044416:
				# max size 16TB
					raise ExecutionError("The file filesize is too large (Max size:16 TB)(%d bytes)" % filesize)
				elif filesize < 0:
					raise ExecutionError("The file filesize should not be negative (%d bytes)" % filesize)
				else:
					print ("%s exists, using its size given (%s bytes)" % (backing_device, filesize))
			elif os.path.exists(backing_device):
					raise ExecutionError("Path %s exists but is not a file" % backing_device)
			else:
				if filesize > 17592186044416:
				# max size 16TB
					raise ExecutionError("The file filesize is too large (Max size:16 TB)(%d bytes)" % filesize)
				elif filesize < 0:
					raise ExecutionError("The file filesize should not be negative (%d bytes)" % filesize)
				else:
					try:
						f = open(backing_device, "w+")
					except (OSError, IOError):
						raise ExecutionError("Could not open %s" % backing_device)
					try:
						try:
							os.posix_fallocate(f.fileno(), 0, filesize)

						except AttributeError:
		                    # Prior to version 3.3, Python does not provide fallocate
							os.ftruncate(f.fileno(), filesize)
					except OverflowError:
						raise ExecutionError("The file size is too large (%d bytes)" % size)

					finally:
						f.close()

			fio = FileIOStorageObject(name = diskname, dev = backing_device, size = filesize)
		elif plugin == 2:
			bio = BlockStorageObject(name = diskname, dev = backing_device)
		else :
			raise ExecutionError ("set plugin is %d now, put 1 or fileio for file; 2 or block for block" % plugin)
		
		return 0

	except Exception,e:

		print e

		return  -1

# def create_backstore(plugin, diskname, backing_device, filesize):
# 	try:

# 		if plugin == 1:
# 			if os.path.isfile(backing_device):
# 				new_size = os.path.getsize(backing_device)
# 				if filesize:
# 					print ("%s exists, using its size (%s bytes) instead" % (backing_device, new_size))
# 				filesize = new_size
# 			elif os.path.exists(backing_device):
# 					raise ExecutionError("Path %s exists but is not a file" % backing_device)
# 			else:
# 				if filesize > 17592186044416:
# 					# max size 16TB
# 					raise ExecutionError("The file filesize is too large (Max size:16 TB)(%d bytes)" % filesize)
# 				elif filesize < 0:
# 					raise ExecutionError("The file filesize should not be negative (%d bytes)" % filesize)
# 				else:
# 					try:
# 						f = open(backing_device, "w+")
# 					except (OSError, IOError):
# 						raise ExecutionError("Could not open %s" % backing_device)
# 					try:
# 						try:
# 							os.posix_fallocate(f.fileno(), 0, filesize)

# 						except AttributeError:
# 		                    # Prior to version 3.3, Python does not provide fallocate
# 							os.ftruncate(f.fileno(), filesize)
# 					except OverflowError:
# 						raise ExecutionError("The file size is too large (%d bytes)" % size)

# 					finally:
# 						f.close()

# 			fio = FileIOStorageObject(name = diskname, dev = backing_device, size = filesize)
# 		elif plugin == 2:
# 			bio = BlockStorageObject(name = diskname, dev = backing_device)
# 		else :
# 			raise ExecutionError ("set plugin is %d now, put 1 or fileio for file; 2 or block for block" % plugin)
		
# 		return 0

# 	except Exception,e:

# 		print e

# 		return  -1
# 	try:
# 		#create target step
# 		iscsiMod = FabricModule('iscsi')

# 		target = Target(iscsiMod, wwn = iqn, mode='lookup')

# 		tpg = TPG(target, tag = tag_index, mode='create')

# 		portal = NetworkPortal(tpg, ip_address, port, mode='any')

# 		if plugin == 1:

# 			fio = FileIOStorageObject(name = diskname)

# 			iscsiMod = FabricModule('iscsi')

# 			target = Target(iscsiMod, wwn = iqn, mode='lookup')

# 			tpg = TPG(target, tag = tag_index, mode='lookup')

# 			lun = LUN(tpg, 0, fio)

# 		elif plugin == 2:

# 			bio = BlockStorageObject(name = diskname)

# 			iscsiMod = FabricModule('iscsi')

# 			target = Target(iscsiMod, wwn = iqn, mode='lookup')

# 			tpg = TPG(target, tag = tag_index, mode='lookup')

# 			lun = LUN(tpg, 0, bio)
# 		else:
# 			print "Can not find correct plugin"

# 			return -1

# 		tpg.enable = enable
	

		
def create_target(iqn):

	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(fabric_module = iscsiMod,wwn = iqn,  mode='create')

		return 0

	except Exception, e:

		print e

		return -1




def create_tpg( iqn, tag_index, ip_address, port):

	try:

		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, wwn = iqn, mode='lookup')

		tpg = TPG(target, tag = tag_index, mode='create')

		portal = NetworkPortal(tpg, ip_address, port, mode='any')

		return 0

	except Exception,e:

		print e

		return -1


def map_target2sobj(iqn, tag_index, plugin, diskname):
	try:
		if plugin == 1:

			fio = FileIOStorageObject(name = diskname)

			iscsiMod = FabricModule('iscsi')

			target = Target(iscsiMod, wwn = iqn, mode='lookup')

			tpg = TPG(target, tag = tag_index, mode='lookup')

			lun = LUN(tpg, 0, fio)

		elif plugin == 2:

			bio = BlockStorageObject(name = diskname)

			iscsiMod = FabricModule('iscsi')

			target = Target(iscsiMod, wwn = iqn, mode='lookup')

			tpg = TPG(target, tag = tag_index, mode='lookup')

			lun = LUN(tpg, 0, bio)

			#print lun.storage_object.delete()

		else:
			print "Can not find correct plugin"

			return -1

		return 0

	except Exception,e:

		print e

		return -1





def enable_tpg(iqn, tag_index , enable):

	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, wwn = iqn, mode='lookup')

		tpg = TPG(target, tag = tag_index, mode='lookup')

		tpg.enable = enable

		return 0

	except Exception,e:

		print e

		return -1





def set_tpg_attr(iqn, tag_index, auth, cach, defa, demo, gene, logi, neti, prod):

	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, wwn = iqn, mode='lookup')

		tpg = TPG(target, tag = tag_index, mode='lookup')

		tpg.set_attribute('authentication', auth)

		tpg.set_attribute('cache_dynamic_acls', cach)
		
		tpg.set_attribute('default_cmdsn_depth', defa)

		tpg.set_attribute('demo_mode_write_protect', demo)

		tpg.set_attribute('generate_node_acls', gene)

		tpg.set_attribute('login_timeout', logi)

		tpg.set_attribute('netif_timeout', neti)

		tpg.set_attribute('prod_mode_write_protect', prod)

		return 0

	except Exception, e:

		print e
 		
 		return -1




def delete_target(del_back, iqn):

	try:
		rtsroot = root.RTSRoot()

		iscsiMod = rtslib.FabricModule('iscsi')

		tgt = rtslib.Target(iscsiMod,iqn,'lookup')

		if del_back == 1:

			for tpg in tgt.tpgs:

				for lun in tpg.luns:

					print ("the %s has been deleted" %(lun.storage_object))
				
					lun.storage_object.delete()

		tgt.delete()

		print ("the %s has been deleted" %(iqn))


		return 0

	except Exception,e:

		print e

		return -1


def delete_backstore(plugin, diskname):

	try:
		if plugin == 1:
			fio = FileIOStorageObject(name = diskname)

			fio.delete()

			print ("the fileio %s has been deleted" %(diskname))


		elif plugin == 2:

			io = BlockStorageObject(name = diskname)

			io.delete()

			print ("the blockio %s has been deleted" %(diskname))

		else:
			return -1
		
		return 0

	except Exception,e:

		print e

		return -1
	


def remove_portals(iqn ,tag_index ,ip_address, port):

	iscsiMod = FabricModule('iscsi')

	target = Target(iscsiMod, iqn, mode='lookup')

	tpg = TPG(target, tag = tag_index, mode = 'any')

	tpg.enable = True

	portal = NetworkPortal(tpg, ip_address, port, mode='lookup')

	portal.delete()


def set_initiator(iqn, tag_index, initi_wwn):

	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, iqn, mode='lookup')
		
		tpg = TPG(target, tag = tag_index, mode = 'any')

		node = NodeACL(tpg, node_wwn = initi_wwn, mode='create')

		tpg.set_attribute('generate_node_acls', 0)

		maplun = MappedLUN(parent_nodeacl = node,mapped_lun = 0,tpg_lun=0)

		return 0

	except RTSLibNotInCFS, e:

		print e

		return -1

	except RTSLibError, e:

		print e

		return -1

def delete_initiator(iqn, tag_index, initi_wwn):

	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, iqn, mode='lookup')

		tpg = TPG(target, tag = tag_index, mode = 'lookup')

		node = NodeACL(tpg, node_wwn = initi_wwn, mode='lookup')

		node.delete()

		return 0

	except Exception, e:

		print e

		return -1
	
# def delete_all_initiator(iqn,tag):
# 	try:
# 		iscsiMod = FabricModule('iscsi')

# 		target = Target(iscsiMod, iqn, mode='lookup')

# 		tpg = TPG(target, tag = tag_index, mode = 'lookup')

# 		for lun in tpg.node_acls:

# 			lun.delete()

# 	except Exception, e:
# 		raise e





# def create_initiator_auth(iqn, tag_index, new_iqn, userid, password):

# 	iscsiMod = FabricModule('iscsi')

# 	target = Target(iscsiMod, iqn, mode = 'lookup')

# 	print list(target.tpgs)

# 	tpg = TPG(target, tag = tag_index, mode = 'any')

# 	tpg.enable = True
	
# 	tpg.set_attribute('authentication', '1')

# 	nodeacl = NodeACL(tpg, 'new_iqn')

# 	nodeacl.chap_userid = userid

# 	nodeacl.chap_password = password





def set_ACLs_mutual_auth(iqn, tag_index, acl_iqn, userid, password, mutual_userid, mutual_password):

	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, iqn, mode = 'lookup')

		tpg = TPG(target, tag = tag_index, mode = 'lookup')

		tpg.enable = True
		
		tpg.set_attribute('authentication', '1')

		tpg.set_attribute('generate_node_acls', '0')

		nodeacl = NodeACL(tpg, acl_iqn,mode='any')

		nodeacl.chap_userid = userid

		nodeacl.chap_password = password

		nodeacl.chap_mutual_userid = mutual_userid

		nodeacl.chap_mutual_password = mutual_password

		return 0

	except Exception,e:

		print e

		return -1


def del_ACLs_mutual_auth(iqn, tag_index):
	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, iqn, mode = 'lookup')

		tpg = TPG(target, tag = tag_index, mode = 'lookup')
		
		tpg.set_attribute('authentication', '0')

		tpg.set_attribute('generate_node_acls', '0')

		return 0

	except Exception,e:

		print e

		return -1




def set_TPG_mutual_auth(iqn, tag_index , userid, password, mutual_userid, mutual_password):

	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, iqn, mode = 'lookup')

		tpg = TPG(target, tag = tag_index , mode = 'lookup')

		tpg.enable = True
		
		tpg.set_attribute('authentication', '1')

		tpg.set_attribute('generate_node_acls', '1')

		tpg.set_attribute('cache_dynamic_acls', '1')

		tpg.set_attribute('demo_mode_write_protect', '0')

		tpg.chap_userid = userid

		tpg.chap_password = password

		tpg.chap_mutual_userid = mutual_userid

		tpg.chap_mutual_password = mutual_password

		return 0

	except Exception,e:

		print e

		return -1

def del_TPG_mutual_auth(iqn, tag_index):

	try:
		iscsiMod = FabricModule('iscsi')

		target = Target(iscsiMod, iqn, mode = 'lookup')

		tpg = TPG(target, tag = tag_index , mode = 'lookup')

		tpg.enable = True
		
		tpg.set_attribute('authentication', '0')

		tpg.set_attribute('generate_node_acls', '1')

		return 0

	except Exception,e:

		print e

		return -1



	




# def creat_discovery_auth(userid, password):

# 	iscsiMod = FabricModule('iscsi')

# 	iscsiMod._set_discovery_enable_auth(enable)

# 	iscsiMod._set_discovery_userid(userid)

# 	iscsiMod._set_discovery_password(password)




# def creat_mutual_discovery_auth(mutual_userid, mutual_password):


# 	iscsiMod = FabricModule('iscsi')

# 	iscsiMod._set_discovery_enable_auth(enable)

# 	iscsiMod._set_discovery_userid(mutual_userid)

# 	iscsiMod._set_discovery_password(mutual_password)





# def create_portals(iqn ,tag_index ,ip_address, port):

# 	iscsiMod = FabricModule('iscsi')

# 	target = Target(iscsiMod, iqn, mode='lookup')

# 	print list(target.tpgs)

# 	tpg = TPG(target, tag = tag_index, mode = 'any')

# 	tpg.enable = True

# 	portal = NetworkPortal(tpg, ip_address, port, mode='create')


def modify_block_size(block_diskname,set_block_size):

	fio = BlockStorageObject(name = block_diskname)

	fio.set_attribute('block_size','set_block_size')

	return fio.get_attribute('block_size')


def delete_all_targets():
	rtsroot = root.RTSRoot()

	print "Before clearconfigs"
	print list(rtsroot.storage_objects)
	print list(rtsroot.targets)

	rtsroot.clear_existing(True)

	print "after clearconfigs"

	return 0
	

	
	

