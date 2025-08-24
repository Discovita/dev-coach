import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
  link: string;
  linkText: string;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'The Coach Philosophy',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Learn about the identity-based life coaching methodology that helps users create 
        and embody their ideal identities across different life areas.
      </>
    ),
    link: '/docs/coach/philosophy',
    linkText: 'Learn More',
  },
  {
    title: 'Core Systems',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Explore the Prompt Manager, Action Handler, and Sentinel systems that power 
        the coaching experience and manage user interactions.
      </>
    ),
    link: '/docs/core-systems/prompt-manager/overview',
    linkText: 'Explore Systems',
  },
  {
    title: 'API Reference',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Complete API documentation for integrating with Dev Coach, including 
        authentication, endpoints, and data models.
      </>
    ),
    link: '/docs/api/overview',
    linkText: 'View APIs',
  },
];

function Feature({title, Svg, description, link, linkText}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
        <Link to={link} className="button button--primary button--sm margin-top--md">
          {linkText}
        </Link>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
