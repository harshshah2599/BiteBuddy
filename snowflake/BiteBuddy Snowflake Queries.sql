use database damg7374;
use schema mart;

show tables in database;


----------------------------------------------------------------------------------------------------
-- Clean Google Reviews --> input for the LLM:
    -- Some pre-processing takes place here
-- drop table damg7374.staging.reviews;
create or replace table damg7374.staging.reviews as 
with restaurants as (
    select gmap_id, 
            name business_name,
            address,
            SPLIT_PART(address, ',', -2) as city
    from damg7374.raw.business
    where contains(category, 'restaurant')
            -- and address ilike'%brookline%'
)
select distinct a.gmap_id,
                a.business_name,
                a.address,
                a.city,
                b.user_id,
                b.rating,
                case when b.text is not null then lower(raw.clean_special_characters(b.text)) else review_text end review_text -- lowercase and special characters removed
from restaurants a
left join damg7374.raw.reviews b on a.gmap_id = b.gmap_id
where review_text is not null;

-- QUERY FOR NEW RESTAURANTS - HAVENT BEEN PROCESSED
select distinct business_name
from damg7374.staging.reviews x
where not exists (select 1
                    from damg7374.staging.sample_reviews
                    where x.business_name = business_name)
                    -- and BUSINESS_NAME ILIKE 'oliveir%'
order by 1;



----------------------------------------------------------------------------------------------------
-- LLM Meal Names and Sentiments from Reviews --> Output of the LLM:
-- drop table damg7374.mart.review_llm_output;
create or replace table damg7374.mart.review_llm_output ( 
    business_name varchar,
    rating numeric, 
    -- review_text varchar,
    -- meals_and_sentiments array,
    meal_name varchar,
    sentiment numeric,
    cluster numeric,
    cluster_label varchar
);

-- Query to get restaurants that have been reviewed
select distinct business_name
from damg7374.mart.review_llm_output
order by business_name;



--------------------------------------------------------------------------
-- Reinforcement Learning from Human Feedback
-- drop table damg7374.mart.bitebuddy_rlhf;
create or replace table damg7374.mart.bitebuddy_rlhf ( 
    business_name varchar,
    meal_name varchar,
    rec_flag boolean,
    create_date date
);

-- Query to get summary of user feedback:
select create_date,
        count(distinct business_name) total_restaurants_feedback,
        count(distinct meal_name) total_meals_feedback,
        count(*) total_feedback,
        sum(case when rec_flag then 1 else 0 end) total_pos_feedback,
        sum(case when rec_flag = FALSE then 1 else 0 end) total_neg_feedback,
        round((total_pos_feedback / total_feedback)*100, 1) as positive_feedback_perc
from damg7374.mart.bitebuddy_rlhf
group by create_date
order by create_date desc;



----------------------------------------------------------------------------------------------------
-- Query that is read by Streamlit App:
-- drop view bitebuddy_recs_fn;
create or replace view damg7374.mart.bitebuddy_recs_fn as
with llm_reviews as (
    select business_name, 
            cluster_label meal_name,
            count(*) total_reviews,
            avg(rating) avg_review_rating,
            avg(REGEXP_REPLACE(sentiment, '[^0-9.]', '')) avg_meal_sentiment
    from damg7374.mart.review_llm_output
    where cluster_label != ''
    group by 1,2 
),
feedback as (
    select business_name,
            meal_name,
            sum(case when rec_flag then 1 else 0 end) total_pos_feedback,
            sum(case when rec_flag = FALSE then 1 else 0 end) total_neg_feedback
    from damg7374.mart.bitebuddy_rlhf
    group by business_name, meal_name
)
select a.*,
        total_pos_feedback,
        total_neg_feedback
from llm_reviews a
left join feedback b on a.business_name = b.business_name and a.meal_name = b.meal_name
;

-- Query to get recommendation metrics 
select * 
from damg7374.mart.bitebuddy_recs_fn
where business_name = 'Rod D by Sitti Thai Cuisine';



----------------------------------------------------------------------------------------------------
-- Store Dietary Responses
-- drop table damg7374.mart.bitebuddy_dietary_responses;
create or replace table damg7374.mart.bitebuddy_dietary_responses ( 
    business_name varchar,
    meal_name varchar,
    dietary_question varchar,
    dietary_response varchar,
    create_date date
);

-- query to get all dietary responses:
select * from damg7374.mart.bitebuddy_dietary_responses;




----------------------------------------------------------------------------------------------------
-- Other Queries:
-- Updating the result output to fix the plural results issue - comines labels for burrito and burritos 
UPDATE damg7374.mart.review_llm_output x
SET CLUSTER_LABEL = LEFT(x.CLUSTER_LABEL, len(x.CLUSTER_LABEL) - 1)
where exists (SELECT 1
             FROM damg7374.mart.review_llm_output
                    WHERE x.CLUSTER_LABEL = CONCAT(CLUSTER_LABEL, 's'))
;





