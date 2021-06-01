#--  create river direction file
##3
if create_rdirc == 1:
    f2 =  netcdf4.Dataset(rdirc, 'r')
    global_attributes  = f2.ncattrs()
    variables = f2.variables
    dimensions = f2.dimensions

    #--  create regional indices
    # rtm
    if rtm_flag == 1:
        xc2  = np.copy(f2.variables['xc'])
        yc2  = np.copy(f2.variables['yc'])
    # mosart
    if rtm_flag == 2:
        xc2  = np.copy(f2.variables['longxy'][:,:])
        yc2  = np.copy(f2.variables['latixy'][:,:])

    #--  convert coordinates to 1d
    rlon=np.asarray(xc2[0,:])
    rlon[rlon < 0] += 360.0
    rlat=np.asarray(yc2[:,0])
    rim=rlon.size
    rjm=rlat.size
    #where returns a tuple, extract list w/ '[0]'
    xind2=np.where((rlon >= ln1) & (rlon <= ln2))[0]
    yind2=np.where((rlat >= lt1) & (rlat <= lt2))[0]
    ni_new=xind2.size
    nj_new=yind2.size

    #--  Check whether file exists  ---------------------------------
    command=['ls',rdirc2]
    file_exists=subprocess.call(command,stderr=subprocess.PIPE)
    if file_exists > 0:
        print('creating new file: ', rdirc2)
    else:
        print('overwriting file: ', rdirc2)

    #--  Open output file
    w = netcdf4.Dataset(rdirc2, 'w', format='NETCDF4')

    #--  Set global attributes
    for ga in global_attributes:
        setattr(w,ga,f2.getncattr(ga))
    #--  Set dimensions of output file
    for dim in dimensions.keys():
        print(dim)
        if dim == 'ncl1' or dim == 'ncl3' or dim == 'ncl5' or dim == 'ncl7' or dim == 'lon':
            w.createDimension(dim,int(ni_new))
        elif dim == 'ncl0' or dim == 'ncl2' or dim == 'ncl4' or dim == 'ncl6' or dim == 'lat':
            w.createDimension(dim,int(nj_new))
        else:
            w.createDimension(dim,len(dimensions[dim]))

    for var in variables.keys():
        y=f2.variables[var].dimensions
        #x2 = [x.encode('ascii') for x in y]
        x2 = y
        vtype = f2.variables[var].datatype
        print(var, vtype, x2)
        wvar = w.createVariable(var, vtype, x2)

        if len(x2) > 1:
            fvar=np.copy(f2.variables[var])
        else:
            fvar=np.copy(f2.variables[var][:])
        #--  Subset input variables
        for n in range(len(x2)):
            fdim = x2[n]
            if fdim == 'ncl1' or fdim == 'ncl3' or fdim == 'ncl5' or fdim == 'ncl7' or fdim == 'lon':
                if n == 0:
                    fvar = fvar[xind2,]
                if n == 1:
                    fvar = fvar[:,xind2,]
                if n == 2:
                    fvar = fvar[:,:,xind2,]
                if n == 3:
                    fvar = fvar[:,:,:,xind2,]
            if fdim == 'ncl0' or fdim == 'ncl2' or fdim == 'ncl4' or fdim == 'ncl6' or fdim == 'lat':
                if n == 0:
                    fvar = fvar[yind2,]
                if n == 1:
                    fvar = fvar[:,yind2,]
                if n == 2:
                    fvar = fvar[:,:,yind2,]
                if n == 3:
                    fvar = fvar[:,:,:,yind2,]

        #--  Set attribute values
        att=f2.variables[var].ncattrs()
        print(att, '\n')
        km=len(att)
        for attname in att:
            print('name: ',attname,' value: ',f2.variables[var].getncattr(attname))
            w.variables[var].setncattr(attname,f2.variables[var].getncattr(attname))

        #--  Set edges to zero
        if var == 'RTM_FLOW_DIRECTION':
            rjm2=fvar.shape[0]
            rim2=fvar.shape[1]
            fvar[:,0]    = 0
            fvar[:,rim2-1] = 0
            fvar[0,:]    = 0
            fvar[rjm2-1.:] = 0

        #--  Write variable data to output file
        if len(wvar.shape) == 1:
            wvar[:] = fvar
        if len(wvar.shape) == 2:
            wvar[:,:] = fvar
        if len(wvar.shape) == 3:
            wvar[:,:,:] = fvar
        if len(wvar.shape) == 4:
            wvar[:,:,:,:] = fvar

    #--  Renumber gridcell indices and downstream indices
    # mosart
    if rtm_flag == 2:
        id_orig = w.variables['ID'][:]
        w.variables['ID'][:] = range(1, id_orig.size+1)
        id_new = w.variables['ID'][:]

        renumber = dict(zip(id_orig.flatten().tolist(), id_new.flatten().tolist()))
        renumber[-9999] = -9999

        dnid = np.asarray(w.variables['dnID'][:])
        dnid_new = dnid.copy()
        dnid_new_vals = [renumber.get(my_id, -99) for my_id in dnid.flatten()]
        dnid_new[:] = np.reshape(dnid_new_vals, dnid_new.shape)
        #print("Number of missing dnID: {}".format(np.sum(dnid_new == -99))))
        dnid_new[dnid_new == -99] = -9999
        w.variables['dnID'][:] = dnid_new

    #--  Close output file
    w.close
