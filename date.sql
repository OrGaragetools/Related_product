/* name - sales_1.xlsx */
SELECT Nomenclature.code2, sales_document
FROM Sales
join Nomenclature on Nomenclature.object_id = Sales.nomenclature_id
WHERE period BETWEEN '15.02.2022' AND '15.02.2023'
GO

/* name - sales_2.xlsx */
SELECT Nomenclature.code2, sales_document
FROM Sales
join Nomenclature on Nomenclature.object_id = Sales.nomenclature_id
WHERE period BETWEEN '16.02.2023' AND '15.02.2024'
GO

/* name - art.xlsx */
SELECT Distinct Nomenclature.code2, count(Distinct(sales_document)) AS quantity_of_sales
FROM Sales
join Nomenclature on Nomenclature.object_id = Sales.nomenclature_id
WHERE period BETWEEN '15.02.2022' AND '15.02.2024'
Group by Nomenclature.code2
GO

