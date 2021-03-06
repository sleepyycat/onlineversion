# coding=UTF-8
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
#import pymongo

from versiononline.models import Product
from versiononline.models import ProductSet
import os.path
import sys
pymongoPath = '/global/share/wuhao/pymongo/pymongo-2.6.3-py2.7-linux-x86_64.egg'
sys.path.append(pymongoPath)
import pymongo
import re


reload(sys)
sys.setdefaultencoding('utf8')


productGroupDict = {'ead_online_version': 1, "search_online_version": 2,
                    "armani_online_version": 4, "infra_online_version": 5, "YNote_online_version": 6 ,
                    "dict_online_version": 7, "fanyi_online_version": 9}

productGroupDictRev = {1: 'ead_online_version', 2: "search_online_version",
                    4: "armani_online_version", 5: "infra_online_version", 6: "YNote_online_version",
                    7: "dict_online_version" , 9: "fanyi_online_version"}

productGroupDictName = {"ead_online_version": "广告","search_online_version":"搜索",
                    "armani_online_version":"购物","infra_online_version":"Infra","YNote_online_version":"笔记",
                    "dict_online_version":"词典","fanyi_online_version":"翻译"}
@csrf_exempt
def onlineversion_info(request):
    try:
        PATH_INFO = request.META['PATH_INFO']
    except KeyError:
        PATH_INFO = 'unknown'
        return HttpResponse("Hello world,Your PATH_INFO is %s" % PATH_INFO)

    #productGroup = PATH_INFO.split('/')[1]
    path_len = len(PATH_INFO.split('/'))
    platformName = str(PATH_INFO.split('/')[1])
    platformId = productGroupDict[platformName]
    platformName_cn = productGroupDictName[platformName]
    if 'action' in request.GET and request.GET['action']:
        action = str(request.GET['action'])

        if action =="add":
            productSetId = int(request.GET['productSetid'])
            productName = request.GET['productName']
            productNameReg = request.GET['productNameReg']
            productSvnReg = request.GET['productSvnReg']
            productSet = ProductSet.objects.filter(id=productSetId,ProductSetStatus=1)[0]
            Product.objects.create(ProductGroup=platformId,ProductSetId=productSet,ProductName=productName ,ProductNameReg=productNameReg,
                                   ProductSvnReg=productSvnReg, ProductStatus=1)
        elif action == "delete":
            productId = int(request.GET['productid'])
            Product.objects.filter(id=productId).update(ProductStatus=0)

        elif action == "add_productSet":
            productSetName = request.GET['productSetName']
            ProductSet.objects.create(ProductGroup=platformId,ProductSetName=productSetName,ProductSetStatus=1)

    productSetList = ProductSet.objects.filter(ProductGroup=platformId, ProductSetStatus=1)
    productsArray=[]
    for productset in productSetList:
        products ={}
        products[0] = Product.objects.filter(ProductSetId=productset.id, ProductStatus=1)
        products[1] = productset.ProductSetName
        products[2] = productset.id
        productsArray.append(products)

    if len(Product.objects.filter(ProductStatus=1,ProductGroup=platformId)) == 0:
        return render_to_response('dateapp/onlineversion_info.html',locals())
    else:
        product = Product.objects.filter(ProductStatus=1,ProductGroup=platformId)[0]
    if path_len == 3:
        productId = int(PATH_INFO.split('/')[2])
        if len(Product.objects.filter(ProductStatus=1,ProductGroup=platformId,id=productId)) == 0:
            return HttpResponseRedirect('/'+platformName)
        product = Product.objects.filter(id=productId,ProductStatus=1)[0]


    productGroup = product.ProductGroup
    productNameReg = product.ProductNameReg
    productSvnReg = product.ProductSvnReg

    client = pymongo.MongoClient('nb396x.corp.youdao.com',27017)
    db = client.ticket
    collection = db.Tickets
    ##测试代码
    #q1 =re.compile(r'resin')
    #q2 = re.compile(r'https://dev.corp.youdao.com/svn/outfox/products/ad/ead/milestones')
    #version_arr = collection.find({"productGroup":productGroup, "product" :{'$regex':r'.*词典.*resin'},"svnPath":{'$regex':q2}})
    #version_arr = collection.find({'$or':[{"productGroup" :1},{"product" :"伏羲系统"}]})
    version_arr = collection.find({"productGroup":productGroup, "product" :{'$regex':productNameReg},"svnPath":{'$regex':productSvnReg}}).sort('svnVersion', pymongo.DESCENDING)
    version_arr_len = version_arr.count()
    #version_arr=[]
    #for item in collection.find({"productGroup":productGroup, "product" :{'$regex':productNameReg},"svnPath":{'$regex':productSvnReg}}).sort({'svnVersion':-1}):
        #version_arr.append(item)



    return render_to_response('dateapp/onlineversion_info.html',locals())

@csrf_exempt
def delete_productSet(request):
    if 'productSetId' in request.POST and request.POST['productSetId']:
        productSetId = int(request.POST['productSetId'])
        ProductSet.objects.filter(id=productSetId).update(ProductSetStatus=0)
        Product.objects.filter(ProductSetId=productSetId).update(ProductStatus=0)
        return HttpResponse("Hello world" )



@csrf_exempt
def edit_product(request):
    try:
        PATH_INFO = request.META['PATH_INFO']
    except KeyError:
        PATH_INFO = 'unknown'
        return HttpResponse("Hello world,Your PATH_INFO is %s" % PATH_INFO)


    productId = int(PATH_INFO.split('/')[3])
    product = Product.objects.filter(id=productId, ProductStatus=1)[0]
    platformName = productGroupDictRev[product.ProductGroup]

    return render_to_response('dateapp/product_edit.html',locals())

@csrf_exempt
def save_product(request):
        platformName=""
        if 'ProductId' in request.POST and request.POST['ProductId']:
            productName = request.POST['productName']
            productNameReg = request.POST['productNameReg']
            productSvnReg = request.POST['productSvnReg']

            ProductGroup = int(request.POST['ProductGroup'])
            ProductSetId = request.POST['ProductSetId']
            ProductId = request.POST['ProductId']
            productSet = ProductSet.objects.filter(id=ProductSetId,ProductSetStatus=1)[0]

            Product.objects.filter(id=ProductId).update(ProductGroup=ProductGroup,ProductSetId=productSet,ProductName=productName ,ProductNameReg=productNameReg,
                                       ProductSvnReg=productSvnReg, ProductStatus=1)
            platformName = productGroupDictRev[ProductGroup]
        return HttpResponseRedirect('/'+platformName)

@csrf_exempt
def add_product_view(request):
    try:
        PATH_INFO = request.META['PATH_INFO']
    except KeyError:
        PATH_INFO = 'unknown'
        return HttpResponse("Hello world,Your PATH_INFO is %s" % PATH_INFO)

    ProductSetId = int(PATH_INFO.split('/')[2])
    ProductGroup = productGroupDict[PATH_INFO.split('/')[1]]
    return render_to_response('dateapp/product_add.html',locals())

@csrf_exempt
def product_add_save(request):
        platformName=""
        if 'productName' in request.POST :
            productName = request.POST['productName']
            productNameReg = request.POST['productNameReg']
            productSvnReg = request.POST['productSvnReg']


            ProductGroup = int(request.POST['ProductGroup'])
            ProductSetId = request.POST['ProductSetId']
            #ProductId = request.POST['ProductId']
            productSet = ProductSet.objects.filter(id=ProductSetId,ProductSetStatus=1)[0]

            Product.objects.create(ProductGroup=ProductGroup,ProductSetId=productSet,ProductName=productName ,ProductNameReg=productNameReg,
                                       ProductSvnReg=productSvnReg, ProductStatus=1)
            platformName = productGroupDictRev[ProductGroup]
        return HttpResponseRedirect('/'+platformName)






