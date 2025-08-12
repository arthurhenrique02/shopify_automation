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
    "mutation customProductCreate($product: ProductCreateInput!, $media: [CreateMediaInput!]) {"
    "    productCreate(product: $product, media: $media) {"
    "        product { "
    "           id "
    "           title"
    "           description"
    "           options { id name position optionValues { id name hasVariants } }"
    "           variants(first: 250) { nodes { id title selectedOptions { name value } } }"
    "           media(first: 10) { nodes { alt mediaContentType status } } "
    "        }"
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
    "mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {"
    "  productVariantsBulkCreate(productId: $productId, variants: $variants) {"
    "    userErrors { field message }"
    "    product { id title options { id name position optionValues { id name hasVariants } } }"
    "    productVariants { id title selectedOptions { name value } }"
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
