#!/usr/bin/env python
# coding: utf-8

# # Examining Job Dissatisfaction In Queensland Education Institutes

# This purpose of this project is to analyze exit surveys from two institutes, the Department of Education, Training, and Employment (DETE), and the Technical and Further Education (TAFE) insitute in Queensland, Australia. The data are available [here](https://data.gov.au/dataset/ds-qld-fe96ff30-d157-4a81-851d-215f2a0fe26d/details?q=exit%20survey) from the government of Australia.

# The questions stakeholders want answers to are:
# Are employees who only worked for the institutes for a short period of time resigning due to some kind of dissatisfaction? What about employees who have been there longer? And:
# Are younger employees resigning due to some kind of dissatisfaction? What about older employees?

# ## Set up

# In[1]:


import pandas as pd
import numpy as np


# ### DETE Survey

# In[2]:


#read in the data
dete_survey = pd.read_csv('dete_survey.csv')

print(dete_survey.info())
dete_survey.head()


# The DETE dataset has 56 columns:

# In[3]:


list(dete_survey.columns)


# Several columns have null values, and the final five columns have mostly null values:

# In[4]:


#print number of null values
dete_survey.isnull().sum()


# We will mainly work with four columns:<br>
# `ID`: An id used to identify the participant of the survey<br>
# `SeparationType`: The reason why the person's employment ended<br>
# `Cease Date`: The year or month the person's employment ended<br>
# `DETE Start Date`: The year the person began employment with the DETE<br>
# These columns have no null values.

# In[5]:


#Examining the final five columns with many missing values:
print(dete_survey['Aboriginal'].value_counts())
print(dete_survey['Torres Strait'].value_counts())
print(dete_survey['South Sea'].value_counts())
print(dete_survey['Disability'].value_counts())
print(dete_survey['NESB'].value_counts())


# So, these five columns, `Aboriginal`, `Torres Strait`, `South Sea`, `Disability`, and `NESB`, either have the response `Yes`, or have the value `NaN`. 

# ### TAFE Survey

# In[6]:


#read in the data
tafe_survey = pd.read_csv('tafe_survey.csv')

print(tafe_survey.info())
tafe_survey.head()


# The TAFE dataset has 72 columns:

# In[7]:


list(tafe_survey.columns)


# The column names are very long, and contain a lot of repetition, punctuation, and sometimes the whole question. They need to be shortened and standardized. Some of them may not be relevant to our questions. 

# In[8]:


#print number of null values
print(tafe_survey.isnull().sum())


# Here we are mainly interested in three columns:<br>
# `Record ID`: An ID used to identify the participant of the survey<br>
# `Reason for ceasing employment`: The reason why the person's employment ended<br>
# `LengthofServiceOverall. Overall Length of Service at Institute (in years)`: The length of the person's employment (in years).
# This last column has 106 missing values.

# In[9]:


#print the number of each value in those 3 columns
print(tafe_survey['Record ID'].value_counts())
print(tafe_survey['Reason for ceasing employment'].value_counts())
print(tafe_survey['LengthofServiceOverall. Overall Length of Service at Institute (in years)'].value_counts())


# We want to compare the datasets, but the column names are completely different, and there are multiple places that indicate an employee was dissatisfied. 

# ## Data Cleaning

# In the DETE dataset, make sure that `Not Stated` values are read in as `NaN` by reading in the data again:

# In[10]:


dete_survey = pd.read_csv('dete_survey.csv', na_values = 'Not Stated')
print(dete_survey.info())


# ### Dropping unnecessary columns

# In the DETE survey, remove columns 28 through 49:

# In[11]:


dete_survey_updated = dete_survey.drop(dete_survey.columns[28:49], axis=1)
dete_survey_updated.head()


# In the TAFE survey, remove columns 17 through 66:

# In[12]:


tafe_survey_updated = tafe_survey.drop(tafe_survey.columns[17:66], axis=1)
tafe_survey_updated.head()


# ### Editing column names

# In the DETE survey, column names have spaces and capitalizations:

# In[13]:


list(dete_survey_updated.columns)


# Make everything lowercase, remove trailing whitespace, and replace spaces with underscores:

# In[14]:


dete_survey_updated.columns = dete_survey_updated.columns.str.lower().str.strip().str.replace(' ', '_')


# Put an underscore in `separationtype`:

# In[15]:


dete_survey_updated = dete_survey_updated.rename({'separationtype':'separation_type'}, axis=1)


# Looking at the updated column names:

# In[16]:


list(dete_survey_updated.columns)


# In the TAFE survey, update column names so that corresponding columns in the two datasets have the same name:

# In[17]:


#create a dictionary to match the old and new column names
mapper = {'Record ID': 'id', 'CESSATION YEAR': 'cease_date', 'Reason for ceasing employment': 'separation_type', 'Gender. What is your Gender?': 'gender', 'CurrentAge. Current Age': 'age', 'Employment Type. Employment Type': 'employment_status', 'Classification. Classification': 'position', 'LengthofServiceOverall. Overall Length of Service at Institute (in years)': 'institute_service', 'LengthofServiceCurrent. Length of Service at current workplace (in years)': 'role_service'}

#rename the columns
tafe_survey_updated = tafe_survey_updated.rename(mapper, axis=1)
list(tafe_survey_updated.columns)


# ### Selecting records of employees who resigned

# In[18]:


dete_survey_updated.head()


# Since our focus is on determining if employees are resigning due to dissatisfaction, we need to select only employees who resigned (from the `separation_type` column):

# In[19]:


dete_survey_updated['separation_type'].value_counts()


# There are three categories for resignation. We will select all of them:

# In[20]:


#rewrites the column - don't run more than once
#cut strings at the dash, so that we are only left with 'Resignation'
dete_survey_updated['separation_type'] = dete_survey_updated['separation_type'].str.split('-').str[0]
dete_survey_updated['separation_type'].value_counts()


# In[21]:


#copy the rows that have resignation as the separation type
dete_resignations = dete_survey_updated[dete_survey_updated['separation_type'] == 'Resignation'].copy()


# In[22]:


dete_resignations.head()


# Now we have a new dataframe, `dete_resignations`, which only includes records of employees who resigned. Now repeating the process for the TAFE survey:

# In[23]:


tafe_survey_updated.head()


# Select only records of employees who resigned:

# In[24]:


tafe_resignations = tafe_survey_updated[tafe_survey_updated['separation_type'] == 'Resignation'].copy()
tafe_resignations.head()


# ### Checking dates

# Check the years in each dataset for inconsistencies: 

# In[25]:


dete_resignations['cease_date'].value_counts()


# The years make sense. However, some rows include a month, but we only want the year.

# In[26]:


#rewrites the column - don't run more than once
#cut strings at the "/" and keep the second part, the year
dete_resignations['cease_date'] = dete_resignations['cease_date'].str.split('/').str[1]
dete_resignations['cease_date'].value_counts()


# Now convert the column type to `float`:

# In[27]:


dete_resignations['cease_date'] = dete_resignations['cease_date'].astype('float64')
dete_resignations['cease_date'].value_counts()


# (it still says int64, not float...)

# Check the `dete_start_date` column for similar issues:

# In[28]:


dete_resignations['dete_start_date'].value_counts(ascending=True)


# The earliest start date is in 1963, which is plausible. The most common start year is 2011. This column appears usable as-is. 

# Checking the years in the TAFE dataset, which only has a `cease_date` column and no start date:

# In[29]:


tafe_resignations['cease_date'].value_counts()


# The cease dates range from 2009-2013. There are much fewer records in 2009, possibly suggesting that data was not collected for the entire year. The DETE survey contained resignations from 2006 to 2014, with some years with no records. 

# ### Length of service

# The TAFE survey already contains a length of service column, `institute_service`, in ranges:

# In[30]:


tafe_resignations['institute_service'].value_counts()


# For the DETE survey, I need to use the `dete_start_date` and  `cease_date` columns to calculate the years of service.

# In[31]:


print(dete_resignations['dete_start_date'].head())
dete_resignations['cease_date'].head()


# Create a new column, also called `institute_survey`, in `dete_resignations`, by subtracting the start date from the end date:

# In[32]:


dete_resignations['institute_service'] = dete_resignations['cease_date'] - dete_resignations['dete_start_date']


# In[33]:


dete_resignations['institute_service'].value_counts()


# To compare to the TEFE survey column, we could re-label these years with the range they fall into. 

# ### Selecting for job dissatisfaction

# In the TAFE survey, there are two columns indicating job dissatisfaction: `Contributing Factors. Dissatisfaction` and `Contributing Factors. Job Dissatisfaction`. 

# In[34]:


print(tafe_resignations['Contributing Factors. Dissatisfaction'].value_counts(dropna=False))
tafe_resignations['Contributing Factors. Job Dissatisfaction'].value_counts(dropna=False)


# The `Contributing Factors. Dissatisfaction` column has the value `Contributing Factors. Dissatisfaction` to indicate dissatisfaction, and a dash otherwise. The `Contributing Factors. Job Dissatisfaction` is the same, except it has the value `Job Dissatisfaction`.

# Replace the strings in the columns with only `True` for dissatisfaction, or `False` or `NaN`: 

# In[35]:


#Create a function to replace the values
def update_vals(myval):
    if (pd.isnull(myval)):
        return np.nan
    elif (myval == '-'):
        return False
    else:
        return True    


# Apply the function to change the values in the two columns indicating dissatisfaction:

# In[36]:


mycols = ['Contributing Factors. Dissatisfaction', 'Contributing Factors. Job Dissatisfaction']
tafe_resignations[mycols] = tafe_resignations[mycols].applymap(update_vals)
tafe_resignations[mycols]


# We want to create one column that will indicate dissatisfaction. We will create a new column, `dissatisfied`, which will have the value `True` if either corresponding value in the two columns above is true. 

# In[37]:


tafe_resignations['dissatisfied'] = tafe_resignations[mycols].any(axis=1, skipna=False)
tafe_resignations['dissatisfied']


# Create a copy of the cleaned dataframe:

# In[38]:


tafe_resignations_up = tafe_resignations.copy()


# In the DETE survey, there are several columns indicating dissatisfaction:
# - `job_dissatisfaction`
# - `dissatisfaction_with_the_department`
# - `physical_work_environment`
# - `lack_of_recognition`
# - `lack_of_job_security`
# - `work_location`
# - `employment_conditions`
# - `work_life_balance`
# - `workload`

# In[39]:


#create a list of the column names
detecols = [
    'job_dissatisfaction',
    'dissatisfaction_with_the_department',
    'physical_work_environment',
    'lack_of_recognition',
    'lack_of_job_security',
    'work_location',
    'employment_conditions',
    'work_life_balance',
    'workload',
]

#select those columns
dete_resignations[detecols]


# The columns already have Boolean values, so we can proceed to creating one column to indicate any dissatisfaction. It will be marked `True` if any of the columns above has a `True` value in that row.

# In[40]:


dete_resignations['dissatisfied'] = dete_resignations[detecols].any(axis=1, skipna=False)
dete_resignations['dissatisfied']


# Make a copy of the dataframe:

# In[41]:


dete_resignations_up = dete_resignations.copy()


# ### Combining the datasets

# First, add a column that will identify which institute the survey came from:

# In[42]:


dete_resignations_up['institute'] = 'DETE'
tafe_resignations_up['institute'] = 'TAFE'


# Combine the dataframes:

# In[43]:


combined = pd.concat([dete_resignations_up, tafe_resignations_up], ignore_index=True)
combined


# Now the two dataframes have been concatonated, with a column identifying which dataset each row originated from.

# ### Grouping length of service

# As mentioned above, the `institute_service` column indicates length of service. The TAFE survey values were in a range, while the DETE survey values were integers. We will reassign them all into new categories modified from [this Business Wire article](https://www.businesswire.com/news/home/20171108006002/en/Age-Number-Engage-Employees-Career-Stage):
# - New: Less than 3 years at a company
# - Experienced: 3-6 years at a company
# - Established: 7-10 years at a company
# - Veteran: 11 or more years at a company

# In[44]:


print(combined['institute_service'].value_counts())
len(combined['institute_service'])


# Where there is a range of numbers, selecting the first number will place it in the correct new group of length of service.

# In[45]:


#before selection
combined['institute_service']


# In[46]:


#use regex (regular expression) pattern r"(\d+)" to select any digit
combined['institute_service'] = (combined['institute_service'].astype('str').str.extract(r"(\d+)").astype('float'))
combined['institute_service'] 


# Create a function that will sort values into the four categories listed above:

# In[47]:


def career_stage(val):
    if pd.isnull(val):
        return np.nan
    elif (val < 3):
        return 'New'
    elif (3 <= val < 7):
        return 'Experienced'
    elif (7 <= val < 11):
        return 'Established'
    else:
        return 'Veteran'


# In[48]:


#apply the function
combined['service_cat'] = combined['institute_service'].apply(career_stage)
combined['service_cat']


# We want to remove columns with less than 500 non-null values, except for `service_cat`. 

# In[49]:


combined['service_cat'].value_counts(dropna=False)


# In[50]:


156+117+71+40 #sum of non-null values


# In[51]:


combined_test_updated = combined.dropna(axis='columns', thresh=500)
list(combined_test_updated.columns)


# So we will only keep the 8 columns listed above, along with `service_cat`:

# In[52]:


combined_updated = combined[['id',
                             'separation_type',
                             'position',
                             'employment_status',
                             'gender',
                             'age',
                             'dissatisfied',
                             'institute',
                             'service_cat']]
combined_updated.head()


# The `institute_service` column had a variety of strings and integers representing the length of service. These have all now been sorted into four categories of employees, `New`, `Experienced`, `Veteran`, `Established`, in the new `service_cat` column. All other columns with less than 500 non-null values have been removed. 

# ### Examining job dissatisfaction

# In[53]:


combined_updated['dissatisfied'].value_counts(dropna=False)


# Fill the null values with `False`:

# In[58]:


combined_updated.loc[:, 'dissatisfied'].copy().fillna(value=False, inplace=True)
#Try using loc like df.loc[:, 'col2'].fillna(df.col1, inplace=True)
combined_updated['dissatisfied'].value_counts(dropna=False)


# In[ ]:


combined_updated['service_cat'].value_counts(dropna=False)


# ## Proportion of resignations due to dissatisfaction by length of service

# To examine job dissatisfaction by length of service, we will make a pivot table giving the percentage of resignations due to dissatisfaction by each of the four length of service categories created above.

# In[ ]:


mypivottable = pd.pivot_table(combined_updated, values='dissatisfied', index=['service_cat'])
mypivottable


# Change order of the pivot table:

# In[ ]:


order = [2,1,0,3]
#create a dictionary and fill in the correct order:
mydata = {'dissatisfied':[]}
for i in order:
    mydata['dissatisfied'].append(mypivottable['dissatisfied'][i])

myindex = ['New', 'Experienced', 'Established', 'Veteran']    
mydf = pd.DataFrame(mydata, index=myindex) #convert to dataframe
mydf


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
mydf.plot(kind='bar', 
             title='Proportion Of Resignations Due To Dissatisfaction by Length of Service',
             legend=False,
             label='Career Stage',
             rot=0.5)


# For these data, `1` represents 100% of the employees who have resigned. As established above, `New` employees have spent less than 3 years at the company, `Experienced` employees  have 3 to 6 years, `Established` ones have 7 to 10, and `Veteran` ones have more than 11 years experience at the company. The barplot shows that of the `Established` employees who left the job, 45% resigned to job dissatisfaction. `New` and `Experienced` employees who resigned were equally likely to give dissatisfaction as the reason (about 27%). `Veteran` employees were more likely to give dissatisfaction as their resignation reason (37%) than `New` and `Experienced` employees, but not as likely as `Established` ones. 

# ### Removing the rest of the missing values

# In[ ]:


print(len(combined_updated))
combined_updated.isnull().sum()


# In[ ]:


#drop rows which contain missing values
combined_updated2 = combined_updated.dropna()


# In[ ]:


combined_updated2


# ### Cleaning the age column

# In[ ]:


combined_updated2['age'].value_counts()


# Once again, the two datasets did not use the same conventions when describing age ranges. One aggregates all ages over 55, while the other combines all ages over 61. Other ages are grouped in ranges of 5 years. Some ranges have dashes and others just have spaces. First we will replace the spaces with dashes. 

# #### Cleaning the age column: test

# First, creating and experimenting on some test data:

# In[ ]:


#create data
mytestdata = {'age': ['51-55', '41 45', '41-45', '56-60', 
              '56 or older', '46 50', '61 or older', 
               '20 or younger'], 'institute': ['TAFE', 
                                               'TAFE', 'TAFE',
                                               'DETE', 'TAFE', 'TAFE',
                                               'DETE', 'TAFE']}
#make it a dataframe
mytestdf = pd.DataFrame(mytestdata)
mytestdf


# Replace every space with a dash (unneccesary ones will be fixed later):

# In[ ]:


mytestdf['age'] = (mytestdf['age'].str.replace(" ", "-"))
mytestdf


# Create a function that will remove the dashes from the strings with words, and replace the variety of categories of people 56 and older with a single category, `56 and older`:

# In[ ]:


def agefunc(val):
    if (val == '56-or-older'):
        return '56 or older'
    elif (val == '56-60'):
        return '56 or older'
    elif (val == '61-or-older'):
        return '56 or older'
    elif (val == '20-or-younger'):
        return '20 or younger'
    else:
        return val


# In[ ]:


mytestdf['age_updated'] = mytestdf['age'].apply(agefunc)
mytestdf


# #### Cleaning the age column: real

# Convert to a pandas dataframe so that the rest of the code works:

# In[ ]:


combined_updated_df = pd.DataFrame(combined_updated2)
combined_updated_df.head()


# Replace every space with a dash (unneccesary ones will be fixed later):

# In[ ]:


combined_updated_df['age'] = (combined_updated_df['age'].str.replace(" ", "-")).str.replace("--", "-")
combined_updated_df['age']


# Create a function that will remove the dashes from the strings with words, and replace the variety of categories of people 56 and older with a single category, `>55`:

# In[ ]:


def agefunc(val):
    if (val == '56-or-older'):
        return '>55'
    elif (val == '56-60'):
        return '>55'
    elif (val == '61-or-older'):
        return '>55'
    elif (val == '20-or-younger'):
        return '<21'
    else:
        return val
    #shortened categories to fit on the graph


# Apply the function:

# In[ ]:


combined_updated_df['age_updated'] = combined_updated_df['age'].apply(agefunc)
combined_updated_df['age_updated'].value_counts()


# ## Proportion of resignations due to dissatisfaction by age

# Create a pivot table with the proportion of resignations due to dissatisfaction by age group:

# In[ ]:


pt_age = pd.pivot_table(combined_updated_df, values='dissatisfied', index=['age_updated'])
pt_age


# Fix the order:

# In[ ]:


order = [7,0,1,2,3,4,5,6,8]
#create a dictionary and fill in the correct order:
age_ordered = {'dissatisfied':[]}
for i in order:
    age_ordered['dissatisfied'].append(pt_age['dissatisfied'][i])

ageindex = ['<21','21-25','26-30','31-35','36-40','41-45',
            '46-50','51-55','>55']   
agedf = pd.DataFrame(age_ordered, index=ageindex) #convert to dataframe
agedf


# Plot the pivot table:

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
agedf.plot(kind='bar', 
             title='Proportion of resignations due to dissatisfaction by age',
             legend=False,
             label='Age',
             rot=0.5)


# The age group with the highest proportion of employees resigning due to dissatisfaction is 31- to 35-year-olds, with nearly 35% resigning due to dissatisfaction. 46- to 55-year-olds come close, with 33% resigning due to dissatisfaction (in both the 46-50 and 51-55 categories). The youngest category (21 and under) was least likely to give dissatisfaction as the reason for their resignation (only 22%).

# ## Comparing dissatisfaction between the DETE and TAFE surveys

# Create a pivot table with the proportion of resignations due to dissatisfaction for each of the two surveys:

# In[ ]:


pt_inst = pd.pivot_table(combined_updated_df, values='dissatisfied', index=['institute'])
pt_inst


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
pt_inst.plot(kind='bar', 
             title='Proportion of resignations due to dissatisfaction by institute',
             legend=False,
             label='Institute',
             rot=0.5)


# Employees from the DETE institute were 1.7 times more likely to list dissatisfaction as the reason for their resignation than employees from the TAFE institute. 

# ## Conclusion

# To restate, the questions stakeholders want answers to are:
# Are employees who only worked for the institutes for a short period of time resigning due to some kind of dissatisfaction? What about employees who have been there longer? And:
# Are younger employees resigning due to some kind of dissatisfaction? What about older employees?

# The first set of questions is answered by the first plot, `Proportion Of Resignations Due To Dissatisfaction by Length of Service`, shows that 45% of resigned employees with 7 to 10 years of experience (`Established` employees) listed some kind of dissatisfaction as the reason, more than any other length of service. `New` (less than 3 years experience) and `Experienced` employees (3 to 6 years experience) who resigned were equally likely to give dissatisfaction as the reason (about 27%). `Veteran` employees (more than 11 years experience) were more likely to give dissatisfaction as their resignation reason (37%) than `New` and `Experienced` employees, but not as likely as `Established` ones. 

# The second set of questions is answered by the second plot, `Proportion of resignations due to dissatisfaction by age`. The youngest employees (21 and under) are least likely to give dissatisfaction as the reason for their resignation (only 22%). The age group with the highest proportion of employees resigning due to dissatisfaction is 31- to 35-year-olds, with nearly 35% resigning due to dissatisfaction. 46- to 55-year-olds come close, with 33% resigning due to dissatisfaction (in both the 46-50 and 51-55 categories).

# In[ ]:




