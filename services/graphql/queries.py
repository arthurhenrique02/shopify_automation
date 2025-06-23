# === COLLECTION QUERIES ===
CREATE_COLLECTION_QUERY = (
    "mutation createCollectionMetafields($input: CollectionInput!) {"
    "    collectionCreate(input: $input) {"
    "    collection { id title }"
    "    userErrors { field message }"
    "}}"
)

PUBLISH_COLLECTION_QUERY = (
    "mutation collectionPublish($collectionId: ID!) {"
    "  collectionPublish(collectionId: $collectionId) {"
    "    collection { id title }"
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

CREATE_VARIANT_QUERY = (
    "mutation productVariantCreate($productId: ID!, $variant: ProductVariantInput!) {"
    "  productVariantCreate(productId: $productId, variant: $variant) {"
    "    productVariant { id title }"
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
