-- Group recipes, add their ratio
WITH menu_sum AS (
    SELECT recipe_id, recipes.name, SUM(multiplier) AS total_multiplier
    FROM menu
    JOIN recipes ON menu.recipe_id = recipes.id
    GROUP BY recipe_id
),
unit_conv AS (
    SELECT menu_sum.name AS name,
	  CASE
	    WHEN ingredient_entry.unit IN ('kg', 'l') THEN 1000 * ingredient_entry.amount * menu_sum.total_multiplier
	    ELSE ingredient_entry.amount * menu_sum.total_multiplier
	  END AS amount,
      CASE
	  WHEN ingredient_entry.unit = 'kg' THEN 'g'
	  WHEN ingredient_entry.unit = 'l' THEN 'ml'
	  ELSE ingredient_entry.unit
	END AS unit,
    ingredient_entry.ingredient_id AS ingredient_id
    FROM menu_sum JOIN ingredient_entry ON menu_sum.recipe_id = ingredient_entry.recipe_id
),
sum_amounts AS(
    SELECT ingredients.name,
	  CASE
	    WHEN unit_conv.unit IN ('g', 'ml') AND SUM(unit_conv.amount) >= 1000 THEN SUM(unit_conv.amount) / 1000
		ELSE SUM(unit_conv.amount) 
	  END AS total_amount,
      CASE
	    WHEN unit_conv.unit = 'g' AND SUM(unit_conv.amount) >= 1000 THEN 'kg'
		WHEN unit_conv.unit = 'ml' AND SUM(unit_conv.amount) >= 1000 THEN 'l'
	    ELSE unit_conv.unit 	
      END AS unit
    FROM ingredients JOIN unit_conv  ON unit_conv.ingredient_id = ingredients.id
    GROUP BY ingredients.name, unit_conv.unit
)
-- Workaround for pivoting
SELECT t1.name, t1.total_amount, t1.unit,
       t2.total_amount, t2.unit,
       t3.total_amount, t3.unit,
       t4.total_amount, t4.unit
FROM sum_amounts t1
  LEFT OUTER JOIN sum_amounts t2 ON t1.name = t2.name AND t1.unit < t2.unit
  LEFT OUTER JOIN sum_amounts t3 ON t1.name = t3.name AND t2.unit < t3.unit
  LEFT OUTER JOIN sum_amounts t4 ON t1.name = t4.name AND t3.unit < t4.unit
GROUP BY t1.name
