import pandas as pd
import matplotlib.pyplot as plt
import operator

# RQ1 #
#which is the rate of complete funnels?
def funnel(ds):
    view_user = ds[ds.event_type == "view"].groupby(['user_id']).count()
    cart_user = ds[ds.event_type == "cart"].groupby(['user_id']).count()
    purchase_user = ds[ds.event_type == "purchase"].groupby(['user_id']).count()
    funnels = view_user.index.intersection(cart_user.index.intersection(purchase_user.index))
    tot_funnels = len(funnels)
    user = len(set(ds['user_id']))  # or: user = len(ds.groupby(['user_id']).count().index)
    rate = tot_funnels / user
    print('The rate of complete funnels is: ', round(rate * 100, 2), '%')

# RQ1 - 1#
#What’s the operation users repeat more on average within a session?
def operation(ds):
    purchase_mean = ds[ds.event_type == "purchase"].groupby(['user_session']).event_type.count().mean()
    view_mean = ds[ds.event_type == "view"].groupby(['user_session']).event_type.count().mean()
    cart_mean = ds[ds.event_type == "cart"].groupby(['user_session']).event_type.count().mean()
    events = ['view', 'cart', 'purchase']
    bars = pd.DataFrame([view_mean, cart_mean, purchase_mean], columns=['event_mean'], index=events)
    bars.plot(kind='bar', rot=0, color=['c'],title="Number of time (in average) a user performs each operation", legend=False, figsize=(8, 6));
    print('Operation that users repeat more on average within a session is: ', events[bars['event_mean'].argmax()])

# RQ1 - 2#
#How many times, on average, a user views a product before adding it to the cart?
def view_cart(ds):
    df_view = ds[ds.event_type == "view"].groupby(['user_id', 'product_id']).count()
    df_cart = ds[ds.event_type == "cart"].groupby(['user_id', 'product_id']).count()
    df_merge = df_view.merge(df_cart, how='inner', left_index=True, right_index=True, suffixes=('_view', '_cart'))
    number_of_views = df_merge['event_type_view'].mean()
    print('The number of times, on average, a user views a product before adding it to the cart is: ',round(number_of_views, 2))

# RQ1 - 3#
#What’s the probability that products added once to the cart are effectively bought?
def prob_cart_bought(ds):
    tot_bought = ds[ds.event_type == "purchase"].groupby(['product_id']).event_type.count().mean()
    tot_added_cart = ds[ds.event_type == "cart"].groupby(['product_id']).event_type.count().mean()
    probability = round(tot_bought / tot_added_cart, 2)
    print('The probability that products added once to the cart are effectively bought is: ', round(probability * 100,2), '%')

# RQ1 - 5#
def take_first(x):
    return x[0]

#How much time passes on average between the first view time and a purchase/addition to cart?
def avg_time(ds):
    cart = ds[ds.event_type == 'cart'].groupby([ds.product_id, ds.user_id]).event_time.unique().to_frame()
    view = ds[ds.event_type == 'view'].groupby([ds.product_id, ds.user_id]).event_time.unique().to_frame()
    view = view.merge(cart, how='inner', left_index=True, right_index=True, suffixes=('_view', '_cart'))
    cart=0
    view = view.applymap(take_first)
    view['event_time_view']=pd.to_datetime(view.event_time_view)
    view['event_time_cart']=pd.to_datetime(view.event_time_cart)
    view['interval']=view['event_time_cart'] - view['event_time_view']
    mean_time = view['interval'].mean()
    print('Time passes on average between the first view time and a purchase/addition to cart: ', mean_time)


# RQ 2 #
#What are the categories of the most trending products overall?
def trend_categories(ds):
    purchase_ds = ds[ds.event_type == "purchase"]
    category_set = purchase_ds[purchase_ds.category_code.notnull()]
    item_sold = category_set['category_code'].value_counts().head(10)

    #What are the 10 most sold products per category?
    for category in item_sold.index.tolist():
        s=category_set[(category_set.category_code==category)].groupby(category_set.product_id).count()
        top_10=s['product_id'].sort_values(ascending=False).head(10)
        print('Most sold products per category: ',top_10)

    item_sold.plot(kind='bar',figsize = (18,6), x = "Category name" , y = "Number of sold products", color='darkorange');
    plt.title("Most visited subcategories", fontsize=15);
    plt.show();

# RQ 3 #
#Write a function that asks the user a category in input
def avg_prod(category,ds):
    #what's the brand whose prices are higher on average?
    avg_price = ds[(ds.event_type == 'purchase') & (ds.category_code == category)].groupby(['brand']).price.mean().sort_values(ascending=False)
    print('Brands in ascending order in category:',avg_price)
    # plot indicating the average price of the products sold by the brand
    avg_price.plot(kind = "bar",figsize=(17, 14), color="blue",title="Average price of the products sold by the brand");
    plt.title("Average price of the products sold by the brand", fontsize = 18);
    plt.xlabel("Brands", fontsize = 18);
    plt.ylabel("Average Price", fontsize = 18);
    for category in ds.category_code.unique():
        max_avg_price = ds[ds.category_code == category].groupby(['brand']).price.mean().idxmax()
        print('The brand with the highest average price in',category,'is:', max_avg_price)

# RQ 4 #
#Write a function that given the name of a brand in input returns, for each month, its profit.
def profit_brand(name_brand, df):
    sum_incomes = df[(df.brand == name_brand) & (df.event_type == 'purchase')].price.sum()
    return sum_incomes

def incomes(ds1,ds2):
    diff = {}
    for brand in ds1['brand'].unique():
        month1 = profit_brand(brand, ds1)
        month2 = profit_brand(brand, ds2)
        difference = month1 - month2
        if difference > 0: #only if month1 is bigger that month2 the brand is at loss
            percentage_difference = difference/month1 * 100
            diff[brand] = percentage_difference
    # Find the top 3 brands that have suffered the biggest losses in earnings between one month and the next, specifing both the loss percentage and the 2 months
    #computing the price.mean() on the datasets and converting them into a list
    incomes1 = ds1.groupby(['brand']).price.mean().sort_values(ascending=True).tolist()
    incomes2 = ds2.groupby(['brand']).price.mean().sort_values(ascending=True).tolist()
    # From the lists I pick the first values (max) and the last values(min), I compute the difference in order to see the difference between the incomes in the two months
    print('Month1 average price max distance:', incomes1[-1] - incomes1[0])
    print('Month2 average price max distance:', incomes2[-1] - incomes2[0])
    sort_orders = sorted(diff.items(), key=lambda x: x[1])
    top_3_brand = sort_orders[-3:] #pick only the percentage difference with higher values
    print('Brands and their losses: \n', *top_3_brand)


# RQ 5 #
def h_avg(ds):
    sort_visited = ds[ds.event_type == 'view'].groupby([ds.event_time.dt.hour]).event_type.count().sort_values(ascending = False).index
    print('In this hour there are more visits on the e-commerce:', sort_visited[0])

    x = ['Monday', 'Tuesday' ,'Wednesday', 'Thursday', 'Friday', 'Saturday' , 'Sunday']
    views = ds[ds.event_type == 'view']
    hour_avg = []
    for i in range (0,7):
        data_Oct_M = views[views.event_time.dt.dayofweek == i]
        hourly_average = (data_Oct_M.event_type.count())/24
        hour_avg.append(hourly_average)

    plt.plot(x, hour_avg, linewidth = 3.0, color='g');
    plt.show();

# RQ 6 #
#What's the overall conversion rate of your online store?
def overall_conversion_rate(ds):
    #look to mean count of viewed and purchased rate of products
    purchases = ds[ds.event_type=='purchase'].event_type.count().sum()
    views = ds[ds.event_type=='view'].event_type.count().sum()
    conversion_rate = (purchases/ views) * 100
    print('The overall conversion rate is:',conversion_rate, '%')

#compute the conversion rate of each category in decreasing order
def categories(ds):
    purchased_category_df = ds[ds.event_type == 'purchase'].groupby(ds['category_code']).event_type.count().sort_values(ascending=False).to_frame()
    all_events = ds.groupby(ds['category_code']).event_type.count().sort_values(ascending=False).to_frame()
    purchase_r = purchased_category_df.merge(all_events, how='inner', left_index=True, right_index=True, suffixes=('_purchase', '_all'))
    purchase_r['purchase_rate'] = purchase_r['event_type_purchase'] / purchase_r['event_type_all']
    view_category_df = ds[ds.event_type == 'view'].groupby(ds['category_code']).event_type.count().sort_values(ascending=False).to_frame()

    cr = purchase_r.merge(view_category_df, how='inner', left_index=True, right_index=True)
    cr['conversion_rate'] = (cr['purchase_rate'] / cr['event_type']) * purchase_r['event_type_all']

    sorted_pr = purchase_r.sort_values(by=['purchase_rate'], ascending=False).purchase_rate
    print('Conversion rate of each category: \n', cr['conversion_rate'])
    sorted_pr[:15].plot(kind='bar', figsize=(20, 8), rot=90, color='purple', fontsize=10);
    plt.title('Number of purchases of each category', fontsize=20);


# RQ 7 #
def pareto_brand(ds):
    # PER BRAND
    sales_df = ds[ds.event_type == "purchase"].groupby([ds.brand]).price.sum().sort_values(ascending=False)
    list_sales = sales_df.tolist()
    tot_sum = sum(list_sales)  #Made the total sum

    cumulative_sum = [0]
    percentage = [0]
    i = 0
    for i in range(len(list_sales)):
        value = list_sales[i]
        cumulative_sum.append(cumulative_sum[-1] + value)
        percentage.append((cumulative_sum[-1] + value) / tot_sum)

    plt.figure(figsize=(8, 8));
    plt.title('5 Best sellers brands', fontsize=15);
    sales_df.head(5).plot.pie(autopct='%.2f%%');

def pareto_category(ds):
    #PER CATEGORY
    sales_df = ds[ds.event_type == "purchase"].groupby([ds.category_code]).price.sum().sort_values(ascending=False)

    list_sales = sales_df.tolist()
    tot_sum = sum(list_sales)
    cumulative_sum = [0]
    percentage = [0]
    i = 0
    for i in range(len(list_sales)):
        value = list_sales[i]
        cumulative_sum.append(cumulative_sum[-1] + value)
        percentage.append((cumulative_sum[-1] + value) / tot_sum)

    plt.figure(figsize=(8, 8));
    plt.title('5 Best sellers categories', fontsize=15);
    sales_df.head(5).plot.pie(autopct='%.2f%%');

def pareto_user(ds):
    # PER USER_ID
    sales_df = ds[ds.event_type == "purchase"].groupby([ds.user_id]).price.sum().sort_values(ascending=False)

    list_sales = sales_df.tolist()
    tot_sum = sum(list_sales)
    cumulative_sum = [0]
    percentage = [0]
    i = 0
    for i in range(len(list_sales)):
        value = list_sales[i]
        cumulative_sum.append(cumulative_sum[-1] + value)
        percentage.append((cumulative_sum[-1] + value) / tot_sum)

    plt.figure(figsize=(8, 8));
    plt.title('5 Best costumers (user_id)', fontsize=15);
    sales_df.head(5).plot.pie(autopct='%.2f%%', colormap='Dark2');
