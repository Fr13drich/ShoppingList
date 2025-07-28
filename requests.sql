WITH menu_sum AS (
    SELECT recipe_id, recipes.name, SUM(multiplier) AS total_multiplier
    FROM menu
    JOIN recipes ON menu.recipe_id = recipes.id
    GROUP BY recipe_id
),
tmp AS (
    SELECT menu_sum.name, ingredient_entry.amount * menu_sum.total_multiplier AS amount, ingredient_entry.unit, ingredient_entry.ingredient_id
    FROM menu_sum JOIN ingredient_entry ON menu_sum.recipe_id = ingredient_entry.recipe_id
)
SELECT ingredients.name, SUM(tmp.amount) AS total_amount, tmp.unit
FROM tmp JOIN ingredients ON tmp.ingredient_id = ingredients.id
GROUP BY ingredients.name, tmp.unit
HAVING total_amount > 0
