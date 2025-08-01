# === COLLECTION QUERIES ===
CREATE_COLLECTION_QUERY = (
    "mutation createCollectionMetafields($input: CollectionInput!) {"
    "    collectionCreate(input: $input) {"
    "    collection { id title }"
    "    userErrors { field message }"
    "}}"
)

PUBLISH_COLLECTION_QUERY = (
    "mutation collectionPublish($input: CollectionPublishInput!) {"
    "  collectionPublish(input: $input) {"
    "    collection { id title }"
    "    collectionPublications { publication { id } }"
    "    userErrors { field message }"
    "  }"
    "}"
)

# === PRODUCT QUERIES ===
CREATE_PRODUCT_QUERY = (
    "mutation productCreate($product: ProductCreateInput!) {"
    "    productCreate(product: $product) {"
    "        product { id title }"
    "        userErrors { field message }"
    "    }"
    "}"
)

CREATE_PRODUCT_MEDIA_QUERY = (
    "mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {"
    "  productCreateMedia(media: $media, productId: $productId) {"
    "    media { alt mediaContentType status }"
    "    mediaUserErrors { field message }"
    "    product { id title }"
    "  }"
    "}"
)

BULK_CREATE_VARIANTS_QUERY = (
    "mutation ProductVariantsCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {"
    "  productVariantsBulkCreate(productId: $productId, variants: $variants) {"
    "    productVariants { id title selectedOptions { name value } }"
    "    userErrors { field message }"
    "  }"
    "}"
)

ADD_PRODUCT_COLLECTION_QUERY = (
    "mutation collectionAddProducts($collectionId: ID!, $productIds: [ID!]!) {"
    "  collectionAddProducts(collectionId: $collectionId, productIds: $productIds) {"
    "    collection { title }"
    "    userErrors { field message }"
    "  }"
    "}"
)

PUBLISH_PRODUCT_QUERY = (
    "mutation productPublish($productId: ID!, $publicationId: ID!) {"
    "  productPublish(productId: $productId, publicationId: $publicationId) {"
    "    product { id title }"
    "    userErrors { field message }"
    "  }"
    "}"
)
