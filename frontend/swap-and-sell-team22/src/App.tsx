import './App.css'
import ProfileIcon from './ProfileIcon'
import Back2menu from './components/back2menu'

function App() {  

  return (
    <>
    <div className="container">
    <div style={{
          backgroundColor: 'green',
          padding: '20px',
          borderRadius: '10px',
          display: 'inline-block',
          width: '400px',
          height: '250px'
        }}>
      <h1 style={{ color: 'white' }}>Swap & Sell: Secondhand Marketplace</h1>
      <Back2menu />
      <ProfileIcon/>
        </div>
        <h1 style={{ color: 'black' }}>I want to...</h1>

        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '40px',
            marginTop: '20px',
          }}
        >
          <a
            href="https://www.google.com/search?q=PLACEHOLDER!!!!!"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              backgroundColor: 'blue',
              color: 'white',
              borderRadius: '50%',
              width: '100px',
              height: '100px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              textDecoration: 'none',
              fontSize: '20px',
              fontWeight: 'bold',
              transition: 'transform 0.2s ease',
            }}
          >
            BUY
          </a>

          <a
            href="https://www.google.com/search?q=PLACEHOLDER!!!!!"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              backgroundColor: 'blue',
              color: 'white',
              borderRadius: '50%',
              width: '100px',
              height: '100px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              textDecoration: 'none',
              fontSize: '20px',
              fontWeight: 'bold',
              transition: 'transform 0.2s ease',
            }}
          >
            SELL
          </a>
        </div>

      </div>
    </>
  )
}

export default App
