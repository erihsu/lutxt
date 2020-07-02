# -*- coding: utf-8 -*-
# @Author: mac
# @Date:   2019-11-02 09:54:23
# @Last Modified by:   eirc
# @Last Modified time: 2019-12-29 15:31:13

import numpy as np 
import os 


class LUT:
	# dependencies:
	# lut.txt(s)
	def __init__(self,file_path):
		self._lutpath = []
		self._slew_lower = 0.0
		self._slew_upper = 0.0
		self._load_lower = 0.0
		self._load_upper = 0.0
		self._lut_slew_index = [] # slew index from lookup table
		self._lut_load_index = [] # cap index from lookup table
		self._buffer_num = 1 # buffer number in the library, must larger than 1
		self._lut_size = []

		self.readlutxt(file_path)
	
	def readlutxt(self,file_path):
		# read prepared lookup table , slew & cap index
		self._lutpath.append(file_path)

		# for read lut_size
		with open(self._lutpath[0],'r') as f: self._lut_size = [int(s) for s in f.readline().strip().split(" ")]

		self._delay_miu_lut   = np.zeros((self._lut_size[0],self._lut_size[1],self._buffer_num))
		self._delay_sigma_lut = np.zeros((self._lut_size[0],self._lut_size[1],self._buffer_num))
		self._slew_miu_lut    = np.zeros((self._lut_size[0],self._lut_size[1],self._buffer_num))
		self._slew_sigma_lut  = np.zeros((self._lut_size[0],self._lut_size[1],self._buffer_num))
		
		for s, lut_file in enumerate(self._lutpath):
			with open(lut_file,'r') as f:
				data = f.readline().strip().split(" ")
				loop1 = int(data[0])
				loop2 = int(data[1])
				for i in range(loop1):
					for j in range(loop2):
						data = f.readline().strip().split(" ")

						if i == 0:
							self._lut_load_index.append(float(data[0]))
						if j == 0:
							self._lut_slew_index.append(float(data[1]))
						
						self._delay_miu_lut[i,j,s] = float(data[2]) # mean value of delay
						self._delay_sigma_lut[i,j,s] = float(data[3]) # standard deviation of delay
						self._slew_miu_lut[i,j,s]  = float(data[4]) # mean value of output slew
						self._slew_sigma_lut[i,j,s] = float(data[5]) # standard deviation of output slew
		
		self._slew_lower, self._slew_upper = self._lut_slew_index.min(), self._lut_slew_index.max()
		self._load_lower, self._load_upper = self._lut_load_index.min(), self._lut_load_index.max()

	def getInputIndex(self,input_slew,output_cap):

		# check input slew
		if input_slew < self._slew_lower or input_slew > self._slew_upper:
			raise Exception("input slew out of bound !")
		
		# check output load 
		if output_cap < self._load_lower or output_cap > self._load_upper:
			raise Exception("output cap out of bound !")

		for i in range(self._lut_size[0] - 1):
			if (input_slew >= self._lut_slew_index[i] and input_slew < self._lut_slew_index[i+1]): slew_index = i
			
		for i in range(self._lut_size[1] - 1):
			if (output_cap >= self._lut_load_index[i] and output_cap < self._lut_load_index[i+1]): cap_index = i
		
		return slew_index, cap_index
	
	def getDelayM(self,input_slew,output_cap,s):
		# get delay from interpolated lookup table

		slew_index,cap_index = self.getInputIndex(input_slew,output_cap)

		r_s = (input_slew-self._lut_slew_index[slew_index])/(self._lut_slew_index[slew_index+1]-self._lut_slew_index[slew_index])
		r_c = (output_cap-self._lut_load_index[cap_index])/(self._lut_load_index[cap_index+1]-self._lut_load_index[cap_index])
			  
		p1 = (1-r_s)*self._delay_miu_lut[slew_index,cap_index,s] + r_s*self._delay_miu_lut[slew_index+1,cap_index,s]
		p2 = (1-r_s)*self._delay_miu_lut[slew_index,cap_index+1,s] + r_s*self._delay_miu_lut[slew_index+1,cap_index+1,s]

		return p1*(1-r_c) + p2*r_c

	def getDelayS(self,input_slew,output_cap,s):
		# get delay sigma from interpolated lookup table

		slew_index,cap_index = self.getInputIndex(input_slew,output_cap)

		r_s = (input_slew-self._lut_slew_index[slew_index])/(self._lut_slew_index[slew_index+1]-self._lut_slew_index[slew_index])
		r_c = (output_cap-self._lut_load_index[cap_index])/(self._lut_load_index[cap_index+1]-self._lut_load_index[cap_index])
			  
		p1 = (1-r_s)*self._delay_sigma_lut[slew_index,cap_index,s] + r_s*self._delay_sigma_lut[slew_index+1,cap_index,s]
		p2 = (1-r_s)*self._delay_sigma_lut[slew_index,cap_index+1,s] + r_s*self._delay_sigma_lut[slew_index+1,cap_index+1,s]

		return p1*(1-r_c) + p2*r_c

	def getSlewM(self,input_slew,output_cap,s):
		# get slew from interpolated lookup table

		slew_index,cap_index = self.getInputIndex(input_slew,output_cap)

		r_s = (input_slew-self._lut_slew_index[slew_index])/(self._lut_slew_index[slew_index+1]-self._lut_slew_index[slew_index])
		r_c = (output_cap-self._lut_load_index[cap_index])/(self._lut_load_index[cap_index+1]-self._lut_load_index[cap_index])
			  
		p1 = (1-r_s)*self._slew_miu_lut[slew_index,cap_index,s] + r_s*self._slew_miu_lut[slew_index+1,cap_index,s]
		p2 = (1-r_s)*self._slew_miu_lut[slew_index,cap_index+1,s] + r_s*self._slew_miu_lut[slew_index+1,cap_index+1,s]

		return p1*(1-r_c) + p2*r_c

	def getSlewS(self,input_slew,output_cap,s):
		# get slew sigma from interpolated lookup table

		slew_index,cap_index = self.getInputIndex(input_slew,output_cap)

		r_s = (input_slew-self._lut_slew_index[slew_index])/(self._lut_slew_index[slew_index+1]-self._lut_slew_index[slew_index])
		r_c = (output_cap-self._lut_load_index[cap_index])/(self._lut_load_index[cap_index+1]-self._lut_load_index[cap_index])
			  
		p1 = (1-r_s)*self._slew_sigma_lut[slew_index,cap_index,s] + r_s*self._slew_sigma_lut[slew_index+1,cap_index,s]
		p2 = (1-r_s)*self._slew_sigma_lut[slew_index,cap_index+1,s] + r_s*self._slew_sigma_lut[slew_index+1,cap_index+1,s]

		return p1*(1-r_c) + p2*r_c
	
	def getAll(self,input_slew,output_cap,size):
		delay 		= self.getDelayM(input_slew,output_cap,size)
		delay_sigma = self.getDelayS(input_slew,output_cap,size)
		slew		= self.getSlewM (input_slew,output_cap,size)
		slew_sigma  = self.getSlewS (input_slew,output_cap,size)
		return delay,delay_sigma,slew,slew_sigma






