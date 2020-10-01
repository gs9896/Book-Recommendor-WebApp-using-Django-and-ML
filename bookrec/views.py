from django.shortcuts import render,redirect
from django.urls import reverse
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from .models import ReadBooks

n=0
bookrating_users = 0
List = 0
List2 = []
List4=[]
def index(request):
    global n
    global bookrating_users
    global List
    global List2
    global List4
    List2.clear()
    List4.clear()
    books=pd.read_csv(r'/home/gurdeep/Downloads/BX-CSV-Dump/BX-Books.csv',sep=';',error_bad_lines=False,warn_bad_lines=False,encoding="latin-1")
    books.columns=['ISBN', 'BookTitle', 'BookAuthor', 'YearOfPublication', 'Publisher','ImageURLS', 'ImageURLM', 'ImageURLL']
    
    users=pd.read_csv('/home/gurdeep/Downloads/BX-CSV-Dump/BX-Users.csv',sep=";",error_bad_lines=False,encoding="latin-1")
    users.columns = ['UserID', 'Location', 'Age']
    
    ratings=pd.read_csv('/home/gurdeep/Downloads/BX-CSV-Dump/BX-Book-Ratings.csv',sep=";",error_bad_lines=False,encoding="latin-1")
    ratings.columns = ['UserID', 'ISBN', 'BookRating']
    
    books.drop(['ImageURLS','ImageURLM','ImageURLL'],axis=1,inplace=True)
    
    bookrating = pd.merge(books,ratings,on='ISBN')
    
    rating_count=pd.DataFrame(bookrating.groupby('BookTitle')['BookRating'].mean())
    rating_count['No of Ratings'] = pd.DataFrame(bookrating.groupby('BookTitle')['BookRating'].count())
    counts=pd.DataFrame(bookrating.groupby('ISBN')['BookRating'].sum())
    counts['BookRatingSum']=counts['BookRating'] 
    counts.drop('BookRating',axis=1,inplace=True)
    
    top_10_books=counts.sort_values(by='BookRatingSum',ascending=False)
    List=top_10_books.merge(books,left_index=True,right_on='ISBN')

    #******************************Similarity using Correlation***************************************
    count_id=bookrating['UserID'].value_counts()  #returns count of occurence of each user ID...thus we get count of users
    count_rate=bookrating['BookTitle'].value_counts()
    bookrating_users=bookrating[bookrating['UserID'].isin(count_id[count_id>=100].index)]  #count>100
    bookrating_users=bookrating_users[bookrating_users['BookTitle'].isin(count_rate[count_rate>=100].index)]

    bookrating_users.sort_values(by='UserID',ascending=False)

    book_matrix=bookrating_users.pivot_table(index='UserID',values='BookRating',columns='BookTitle')
    if request.user.is_authenticated:
            if ReadBooks.objects.filter(username=request.user.username).exists():
                books=ReadBooks.objects.filter(username=request.user.username).values()
                for obj in books:
                    reads=obj["read"]
                    List4.append(reads)
    
                    wildanimus_user_ratings = book_matrix[reads]

                    similar_to_wildanimus = book_matrix.corrwith(wildanimus_user_ratings)

                    corr_wildanimus = pd.DataFrame(similar_to_wildanimus,columns=['Correlation'])
                    corr_wildanimus.dropna(inplace=True)

                    corr_wildanimus.sort_values('Correlation',ascending=False).head()

                    corr_wildanimus = corr_wildanimus.join(rating_count['No of Ratings'])
                    corr_wildanimus.sort_values('Correlation',ascending=False)

                    correlation_lb=corr_wildanimus[corr_wildanimus['No of Ratings']>200].sort_values('Correlation',ascending=False).head()

                    List2=List2+correlation_lb.index.to_list()
                    List2=set(List2)
                    List2=list(List2)

    if request.method == 'POST' and 'next' in request.POST:
        n=n+10 
    elif request.method == 'POST' and 'prev' in request.POST:
        if(n!=0):
            n=n-10
    else:
        n=0
    List4=set(List4)
    List4=list(List4)
    return render(request,'index.html',{"Topbooks":List[n:(n+10)],"Simlarity":List2[:10],"Explored":List4[:10]})


def saveread(request,bookread):        
    if request.user.is_authenticated:
        if ReadBooks.objects.filter(read=bookread).exists():
            return redirect(index)
        else:
            newbook = ReadBooks(username=request.user.username, read=bookread)
            newbook.save()
    return redirect(index)

def search(request):
    global bookrating_users
    global List
    global List2
    global List4
    global n
    book_matrix_new=bookrating_users.pivot_table(index='BookTitle',values='BookRating',columns='UserID')
    book_matrix_new=book_matrix_new.fillna(0)
    book_matrix_matrix= csr_matrix(book_matrix_new.values)

    model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')  # metric used for evaluation is cosine
    model_knn.fit(book_matrix_matrix)  #fitting model with matrix

    if request.method == 'POST':
        search = request.POST.get("search")
        title_list=book_matrix_new.index.to_list()
        l_search=search.lower()
        l_title_list = list(map(lambda x:x.lower(), title_list))
        if(l_search in l_title_list):
            random_index = l_title_list.index(l_search)  #generating random book indices out of the book_matrix
            distances, indices = model_knn.kneighbors(book_matrix_new.iloc[random_index,:].values.reshape(1, -1), n_neighbors = 8)
            List3=book_matrix_new.index[indices.flatten()].to_list()
 
        else:
            List3 = ["No Result Found !!"]
    return render(request,'index.html',{"searchres":List3,"Topbooks":List[n:(n+10)],"Simlarity":List2[:10],"Explored":List4[:10]})