# a = [(1,2), (5,6), (7,8), (9,10)]

# a = a.sort(key = lambda x: x[1])

# print(a)
# fun = lambda x:x*x
# mylist = [1,3,4,2,0.5]

# mylist = map(fun, mylist)

# print(list(mylist))


# numbers = [10,11,8,6,100, 7 , 9 , 21]

# numbers = map(lambda x:"big" if x>10 else "small", numbers)
# print(list(numbers))    

# mylist = [1,5,6,8,10,11]


# print(list(filter(lambda x:x%2==0,mylist)))
# Task 1: Write a function that takes a list of 
# numbers and returns a new list containing only 
# the squares of the even numbers from the original list. 
# Use map, filter, and lambda to accomplish this.

# mylist = [1,2,3,4,5,6,7,8,9]

# newList = map(lambda x: x*x ,filter(lambda x:x%2!=0 , mylist))

# print(list(newList))

# Task 2: Write a function that takes a list of strings and returns a new list containing only 
# the strings that have an even number of characters, converted to uppercase. Use map, filter, and 
# lambda to accomplish this.

mylist = ["abdullah", "ali", "ali","faqir","fawad","salim","sherzad"]

newList = map(lambda x: x.upper() ,filter(lambda x:len(x)%2==0 , mylist))

print(list(newList))