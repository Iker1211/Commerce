from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, Category, List, Comment, Bid


def listing(request, id):
    listingData = List.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner
    })

def closeAuction(request, id):
    listingData = List.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "The auction has been closed"
    })

def addBid(request, id):
    newBid = request.POST.get("newBid")
    listingData = List.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    if int(newBid) > listingData.price.bid:
        updateBid = Bid(user=request.user, bid=int(newBid))
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Your bid has been placed",
            "update": True,
            "isOwner": isOwner,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments
        }) 
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Your bid must be higher than the current bid",
            "update": False,
            "isOwner": isOwner,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments
        }) 

def addComment(request, id):
    if request.method == "POST":
        new_comment = request.POST.get("newComment")
        listing = get_object_or_404(List, pk=id)
        comment = Comment(user=request.user, listing=listing, comment=new_comment)
        comment.save()
        return HttpResponseRedirect(reverse("listing", args=(id,)))
    

def watchlist(request):
    currentUser = request.user
    listings = currentUser.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def removeWatchlist(request, id):
    listingData = List.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def addWatchlist(request, id):
    listingData = List.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))


def index(request):
    activeListings = List.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
    })


def displayCategory(request):
    if request.method == "POST":
        categoryForm = request.POST["category"]
        category = Category.objects.get(categoryName=categoryForm)
    activeListings = List.objects.filter(isActive=True, category=category)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
    })

def createList(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render (request, "auctions/createList.html", {
            "categories": allCategories
        })
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imageUrl = request.POST["imageurl"]
        price = request.POST["price"]
        category_name = request.POST["category"]
        userNow = request.user

        categoryData = Category.objects.get(categoryName=category_name)
        #Create a bid object
        bid_instance = Bid.objects.create(bid=price, user=userNow)
        bid_instance.save()
        # Create a new list
        newList = List(
            title=title,
            description=description,
            imageUrl=imageUrl,
            price=bid_instance,
            category=categoryData,
            owner=userNow
            )

        newList.save()

        return HttpResponseRedirect(reverse("index"))



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
