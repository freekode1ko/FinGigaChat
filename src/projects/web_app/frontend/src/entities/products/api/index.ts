import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, API_TAGS } from '@/shared/model'

import type { CreateProduct, Product } from '../model'
import { CreateProductDocument } from '../model/types'

const productsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getProductsTree: build.query<Array<Product>, void>({
      query: () => ({
        url: API_ENDPOINTS.products + '/tree',
        method: 'GET',
      }),
      providesTags: [API_TAGS.products],
      keepUnusedDataFor: 300,
    }),
    getProducts: build.query<Array<Product>, void>({
      query: () => ({
        url: API_ENDPOINTS.products + '/',
        method: 'GET',
      }),
    }),
    createProduct: build.mutation<string, CreateProduct>({
      query: (body) => ({
        url: `${API_ENDPOINTS.products}/`,
        method: 'POST',
        body: body,
      }),
      invalidatesTags: [API_TAGS.products],
    }),
    updateProduct: build.mutation<
      string,
      { product: CreateProduct; id: number }
    >({
      query: ({ product, id }) => ({
        url: `${API_ENDPOINTS.products}/` + id,
        method: 'PATCH',
        body: product,
      }),
      invalidatesTags: [API_TAGS.products],
    }),
    deleteProduct: build.mutation<string, { id: number }>({
      query: ({ id }) => ({
        url: `${API_ENDPOINTS.products}/` + id,
        method: 'DELETE',
      }),
      invalidatesTags: [API_TAGS.products],
    }),
    uploadProductDocument: build.mutation<
      string,
      { document: CreateProductDocument; productId: number }
    >({
      query({ document, productId }) {
        const formData = new FormData()
        if (document.file) formData.append('file', document.file)
        formData.append('name', document.name)
        if (document.description)
          formData.append('description', document.description)
        return {
          url: `${API_ENDPOINTS.products}/` + productId + '/documents',
          method: 'POST',
          body: formData,
        }
      },
      invalidatesTags: [API_TAGS.products],
    }),
  }),
})

export const {
  useGetProductsTreeQuery,
  useGetProductsQuery,
  useCreateProductMutation,
  useDeleteProductMutation,
  useUpdateProductMutation,
  useUploadProductDocumentMutation,
} = productsApi
