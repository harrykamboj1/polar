import Current from '@/components/Finance/IssueFunding/Current'
import { getServerSideAPI } from '@/utils/api/serverside'
import { getOrganizationBySlugOrNotFound } from '@/utils/organization'
import { Metadata } from 'next'

const cacheConfig = {
  next: {
    revalidate: 30, // 30 seconds
  },
}

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: 'Finance - Issue funding', // " | Polar is added by the template"
  }
}

export default async function Page({
  params,
}: {
  params: { organization: string }
}) {
  const api = getServerSideAPI()
  const organization = await getOrganizationBySlugOrNotFound(
    api,
    params.organization,
    cacheConfig,
  )

  return <Current organization={organization} />
}
