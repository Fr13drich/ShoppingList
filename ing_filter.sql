WITH ing_set AS (
SELECT id from ingredients where name like ?
)
SELECT DISTINCT name FROM ing_set
JOIN ingredient_entry ON ingredient_entry.ingredient_id = ing_set.id
JOIN recipes ON recipes.id = recipe_id
ORDER BY name
