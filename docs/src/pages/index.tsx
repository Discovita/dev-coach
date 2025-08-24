import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          Dev Coach Documentation
        </Heading>
        <p className="hero__subtitle">
          Complete guide to the AI-powered life coaching system that helps users create and maintain multiple identities for different areas of their lives
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Reading 📚
          </Link>
          <Link
            className="button button--outline button--lg"
            to="/docs/coach/philosophy"
            style={{marginLeft: '1rem'}}>
            Learn the Philosophy 🎯
          </Link>
        </div>
      </div>
    </header>
  );
}

function QuickNavigation() {
  return (
    <section className="padding-vert--xl">
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <Heading as="h2" className="text--center margin-bottom--lg">
              Quick Navigation
            </Heading>
          </div>
        </div>
        <div className="row">
          <div className="col col--4 margin-bottom--lg">
            <div className="card">
              <div className="card__header">
                <Heading as="h3">🎯 The Coach</Heading>
              </div>
              <div className="card__body">
                <p>Learn about the coaching philosophy, techniques, and identity categories.</p>
                <Link to="/docs/coach/philosophy" className="button button--primary button--sm">
                  Explore Philosophy
                </Link>
              </div>
            </div>
          </div>
          <div className="col col--4 margin-bottom--lg">
            <div className="card">
              <div className="card__header">
                <Heading as="h3">⚙️ Core Systems</Heading>
              </div>
              <div className="card__body">
                <p>Understand the Prompt Manager, Action Handler, and Sentinel systems.</p>
                <Link to="/docs/core-systems/prompt-manager/overview" className="button button--primary button--sm">
                  View Systems
                </Link>
              </div>
            </div>
          </div>
          <div className="col col--4 margin-bottom--lg">
            <div className="card">
              <div className="card__header">
                <Heading as="h3">🔌 API Reference</Heading>
              </div>
              <div className="card__body">
                <p>Complete API documentation for integration and development.</p>
                <Link to="/docs/api/overview" className="button button--primary button--sm">
                  Browse APIs
                </Link>
              </div>
            </div>
          </div>
        </div>
        <div className="row">
          <div className="col col--4 margin-bottom--lg">
            <div className="card">
              <div className="card__header">
                <Heading as="h3">🗄️ Database</Heading>
              </div>
              <div className="card__body">
                <p>Database models, schema, and relationships for the Dev Coach system.</p>
                <Link to="/docs/database/overview" className="button button--primary button--sm">
                  View Schema
                </Link>
              </div>
            </div>
          </div>
          <div className="col col--4 margin-bottom--lg">
            <div className="card">
              <div className="card__header">
                <Heading as="h3">🛠️ How-To Guides</Heading>
              </div>
              <div className="card__body">
                <p>Step-by-step guides for adding new features and extending the system.</p>
                <Link to="/docs/how-to/overview" className="button button--primary button--sm">
                  Read Guides
                </Link>
              </div>
            </div>
          </div>
          <div className="col col--4 margin-bottom--lg">
            <div className="card">
              <div className="card__header">
                <Heading as="h3">🧪 Testing</Heading>
              </div>
              <div className="card__body">
                <p>Testing strategies and tools for the Dev Coach platform.</p>
                <Link to="/docs/testing/overview" className="button button--primary button--sm">
                  Learn Testing
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="Comprehensive documentation for the Discovita Dev Coach system - an AI-powered life coaching platform that helps users create and maintain multiple identities for different areas of their lives.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <QuickNavigation />
      </main>
    </Layout>
  );
}
